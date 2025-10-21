import os
import math
import pygame
import pandas as pd
from tkinter import Tk, filedialog

from components.ui_base import (
    COR_FUNDO_BASE, COR_DESTAQUE, COR_TEXTO,
    ajustar_claridade, draw_rounded_rect, draw_shadow, draw_vignette,
    Botao
)

def wrap_text(surface, text, font, max_width):
    """Quebra de linha com elipse final se ultrapassar muitas linhas."""
    if not text:
        return [""]
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def elide_text(font, text, max_width):
    """Corta com '…' se passar do tamanho."""
    if font.size(text)[0] <= max_width:
        return text
    ell = "…"
    # busca binária no tamanho
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        t = text[:mid] + ell
        if font.size(t)[0] <= max_width:
            lo = mid + 1
        else:
            hi = mid
    return text[:max(0, lo - 1)] + ell

class TelaPlanilha:
    def __init__(self, surface, on_voltar):
        self.surface = surface
        self.on_voltar = on_voltar

        self.titulo = 'Análise de Planilha'
        self.arquivo = None
        self.resultado_linhas = []
        self.scroll_y = 0

        # Botões
        self.bt_escolher = Botao('Escolher Planilha', self.escolher_arquivo)
        self.bt_analisar = Botao('Analisar', self.analisar)
        self.bt_voltar   = Botao('← Voltar', self.on_voltar)
        self.botoes = [self.bt_escolher, self.bt_analisar, self.bt_voltar]

        # Layout vars
        self.fonte_botoes = None
        self.fonte_titulo = None
        self.fonte_relatorio = None

        self.btn_rects = []
        self.legend_lines = []
        self.legend_pos = (0, 0)
        self.card_rect = None
        self.area_relatorio = None

        self.recalcular_layout()

    # ---------------- UI/Layout ----------------
    def _btn_columns(self, w):
        """Decide colunas dos botões por largura da janela."""
        if w >= 980:    # largo: 3 em linha
            return 3
        if w >= 680:    # médio: 2 colunas
            return 2
        return 1        # estreito: 1 coluna

    def recalcular_layout(self):
        w, h = self.surface.get_size()

        # Margens e métricas responsivas
        margin = max(16, int(min(w, h) * 0.04))
        # Título
        self.fonte_titulo = pygame.font.SysFont('Arial', max(20, int(h * 0.05)), bold=True)

        # Botões
        cols = self._btn_columns(w)
        gap_h = max(10, int(h * 0.015))
        gap_w = max(10, int(w * 0.02))
        btn_h = max(48, int(h * 0.085))
        self.fonte_botoes = pygame.font.SysFont('Arial', max(16, int(btn_h * 0.42)), bold=True)

        # Tentativa de largura base por coluna
        avail_w = w - 2 * margin - (cols - 1) * gap_w
        btn_w = max(120, min(280, int(avail_w / cols)))

        # Linha(s) de botões — pode virar grid 2x2 no médio/pequeno
        titulo_h = self.fonte_titulo.get_height()
        y_start = margin - 4 + titulo_h + max(6, int(h * 0.01))

        self.btn_rects = []
        rows = math.ceil(len(self.botoes) / cols)
        for i, b in enumerate(self.botoes):
            r = i // cols
            c = i % cols
            # centraliza a grade
            row_w = cols * btn_w + (cols - 1) * gap_w
            x0 = (w - row_w) // 2
            x = x0 + c * (btn_w + gap_w)
            y = y_start + r * (btn_h + gap_h)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.btn_rects.append(rect)
            b.rect = rect

        # Legenda (logo abaixo dos botões)
        legend_y = y_start + rows * (btn_h + gap_h)
        self.fonte_relatorio = pygame.font.SysFont('Consolas, Menlo, Courier New, monospace', max(14, int(h * 0.022)))
        leg_text = f'Arquivo: {os.path.basename(self.arquivo) if self.arquivo else "nenhum selecionado"}'

        # largura da legenda: da borda esquerda até a borda direita da grade
        if self.btn_rects:
            left = min(r.x for r in self.btn_rects)
            right = max(r.right for r in self.btn_rects)
        else:
            left, right = margin, w - margin
        leg_max_w = max(160, right - left)

        # quebrar em até 2 linhas; se ainda passar, corta com …
        lines = wrap_text(self.surface, leg_text, self.fonte_relatorio, leg_max_w)
        if len(lines) > 2:
            lines = lines[:2]
            lines[-1] = elide_text(self.fonte_relatorio, lines[-1], leg_max_w)
        self.legend_lines = lines
        self.legend_pos = (left, legend_y)

        # Card do relatório
        legend_height = len(self.legend_lines) * (self.fonte_relatorio.get_height() + 2)
        card_y = legend_y + legend_height + 10
        card_h = h - card_y - margin
        self.card_rect = pygame.Rect(margin, card_y, w - 2 * margin, max(140, card_h))

        pad = max(14, int(min(w, h) * 0.02))
        self.area_relatorio = pygame.Rect(
            self.card_rect.x + pad,
            self.card_rect.y + pad,
            self.card_rect.w - 2 * pad,
            self.card_rect.h - 2 * pad
        )

        # reset de scroll se área mudou muito
        self.scroll_y = min(0, self.scroll_y)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.recalcular_layout()
        elif event.type == pygame.MOUSEWHEEL:
            self._scroll(event.y * 26)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_k):
                self._scroll(20)
            elif event.key in (pygame.K_DOWN, pygame.K_j):
                self._scroll(-20)
            elif event.key == pygame.K_PAGEUP:
                self._scroll(self.area_relatorio.h // 1.5)
            elif event.key == pygame.K_PAGEDOWN:
                self._scroll(-self.area_relatorio.h // 1.5)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.botoes: b.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self.botoes:
                if b.pressed:
                    b.pressed = False
                    b.checar_clique(event.pos)

    def _scroll(self, dy):
        self.scroll_y += dy
        limite = -max(0, len(self.resultado_linhas)* (self.fonte_relatorio.get_height()+6) - self.area_relatorio.h)
        self.scroll_y = max(min(self.scroll_y, 0), limite)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for b in self.botoes:
            b.atualizar_hover(mouse_pos)

    def draw(self):
        import components.ui_base as ui_base

        self.surface.fill(COR_FUNDO_BASE)
        draw_vignette(self.surface)

        # Título
        titulo_render = self.fonte_titulo.render(self.titulo, True, (87, 11, 98))
        titulo_x = (self.surface.get_width() - titulo_render.get_width()) // 2
        margin = max(16, int(min(*self.surface.get_size()) * 0.04))
        self.surface.blit(titulo_render, (titulo_x, margin - 4))

        # Botões
        for b in self.botoes:
            b.desenhar(self.surface, self.fonte_botoes)

        # Legenda (2 linhas no máx)
        x_leg, y_leg = self.legend_pos
        for i, ln in enumerate(self.legend_lines):
            render = self.fonte_relatorio.render(ln, True, COR_TEXTO)
            self.surface.blit(render, (x_leg, y_leg + i * (self.fonte_relatorio.get_height() + 2)))

        # Card do relatório
        card_surf = pygame.Surface(self.card_rect.size, pygame.SRCALPHA)
        for i in range(self.card_rect.height):
            alpha = int(ui_base.lerp(90, 140, i / max(1, self.card_rect.height - 1)))
            pygame.draw.rect(card_surf, (255, 255, 255, alpha), (0, i, self.card_rect.width, 1))
        mask = pygame.Surface(self.card_rect.size, pygame.SRCALPHA)
        draw_rounded_rect(mask, mask.get_rect(), (255, 255, 255, 0), radius=24)
        card_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        draw_shadow(self.surface, self.card_rect, radius=28, offset=(0, 10), alpha=90)
        self.surface.blit(card_surf, self.card_rect)
        pygame.draw.rect(self.surface, ajustar_claridade(COR_DESTAQUE, 1.4),
                         self.card_rect, width=2, border_radius=24)

        # Texto do relatório com clip + scroll
        clip_old = self.surface.get_clip()
        self.surface.set_clip(self.area_relatorio)

        y_texto = self.area_relatorio.y + self.scroll_y
        lh = self.fonte_relatorio.get_height() + 6
        for linha in self.resultado_linhas:
            render = self.fonte_relatorio.render(linha, True, (40, 40, 40))
            self.surface.blit(render, (self.area_relatorio.x, y_texto))
            y_texto += lh

        self.surface.set_clip(clip_old)
        pygame.draw.rect(self.surface, ajustar_claridade(COR_TEXTO, 1.2),
                         self.area_relatorio, width=2, border_radius=10)

    # ---------------- Ações ----------------
    def escolher_arquivo(self):
        try:
            root = Tk(); root.withdraw(); root.wm_attributes('-topmost', 1)
            caminho = filedialog.askopenfilename(
                title='Selecione a planilha',
                filetypes=[('Planilhas', '*.xlsx *.xls *.csv'), ('Todos', '*.*')]
            )
            root.destroy()
        except Exception as e:
            self.resultado_linhas = [f'Erro ao abrir seletor de arquivos: {e}']
            return

        if caminho:
            self.arquivo = caminho
            base = os.path.basename(self.arquivo)
            self.resultado_linhas = [f'Arquivo selecionado: {base}',
                                     'Clique em "Analisar" para continuar.']
            self.scroll_y = 0
            self.recalcular_layout()  # atualiza legenda com nome novo

    def analisar(self):
        if not self.arquivo:
            self.resultado_linhas = ['Nenhum arquivo selecionado. Clique em "Escolher Planilha" primeiro.']
            return

        try:
            ext = os.path.splitext(self.arquivo)[1].lower()
            if ext in ('.xlsx', '.xls'):
                xls = pd.ExcelFile(self.arquivo)
                linhas = [f'📄 Tipo: Excel ({ext})',
                          f'📚 Abas: {len(xls.sheet_names)} -> {", ".join(xls.sheet_names[:8])}'
                          + ('...' if len(xls.sheet_names) > 8 else '')]
                df = xls.parse(xls.sheet_names[0])
                linhas += self._sumarizar_df(df, nome_aba=xls.sheet_names[0])

            elif ext == '.csv':
                df = pd.read_csv(self.arquivo, nrows=50000)
                linhas = [f'📄 Tipo: CSV',
                          f'📦 Linhas lidas (amostra ou total): {len(df):,}'.replace(',', '.')]
                linhas += self._sumarizar_df(df)
            else:
                linhas = [f'Formato não suportado: {ext}', 'Suporte: .xlsx, .xls, .csv']

            self.resultado_linhas = linhas
            self.scroll_y = 0

        except Exception as e:
            self.resultado_linhas = [f'Erro na análise: {e}']

    # ---------------- Helpers ----------------
    def _sumarizar_df(self, df, nome_aba=None):
        linhas = []
        if nome_aba:
            linhas.append(f'🗂️  Aba analisada: {nome_aba}')
        linhas.append(f'🔢 Dimensão: {df.shape[0]:,} linhas x {df.shape[1]:,} colunas'.replace(',', '.'))

        cols = list(map(str, df.columns.tolist()))
        linhas.append('🧾 Colunas: ' + (', '.join(cols[:8]) + ('...' if len(cols) > 8 else '')))

        tipos = df.dtypes.astype(str).to_dict()
        linhas.append('🔠 Tipos (amostra): ' + ', '.join([f'{k}:{v}' for k, v in list(tipos.items())[:8]])
                      + ('...' if len(tipos) > 8 else ''))

        nulos = df.isna().sum().sort_values(ascending=False)
        top_nulos = [(c, int(n)) for c, n in nulos.head(8).items() if n > 0]
        if top_nulos:
            linhas.append('⚠️ Nulos (top 8): ' + ', '.join([f'{c}:{n}' for c, n in top_nulos]))
        else:
            linhas.append('✅ Sem valores nulos.')

        num_cols = df.select_dtypes(include='number')
        if not num_cols.empty:
            linhas.append('📊 Numéricas (amostra):')
            desc = num_cols.describe().round(2).to_dict()
            mostradas = 0
            for col, stats in desc.items():
                if mostradas >= 5: break
                linhas.append(f'  • {col} -> min:{stats.get("min")}, média:{stats.get("mean")}, '
                              f'mediana:{num_cols[col].median():.2f}, max:{stats.get("max")}')
                mostradas += 1
        return linhas
