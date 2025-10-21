import pygame
import sys
import os

from components.ui_base import (
    COR_FUNDO_BASE, COR_DESTAQUE, ajustar_claridade,
    draw_rounded_rect, draw_shadow, draw_vignette,
    Botao, calcular_layout
)

# Importa a tela de planilha
from screens.planilha import TelaPlanilha

pygame.init()

LARGURA_INICIAL, ALTURA_INICIAL = 500, 600
tela = pygame.display.set_mode((LARGURA_INICIAL, ALTURA_INICIAL), pygame.RESIZABLE)
pygame.display.set_caption('Maria Pitanga - Açaí e Gelatos')

# Carrega fundo (opcional)
ARQ_IMAGEM = 'img.png'
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
CAMINHO_IMAGEM = os.path.join(BASE_DIR, ARQ_IMAGEM)

bg_image = None
if os.path.exists(CAMINHO_IMAGEM):
    try:
        bg_image = pygame.image.load(CAMINHO_IMAGEM).convert()
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")

def escalar_fundo(img, tamanho):
    if not img:
        return None
    largura, altura = tamanho
    return pygame.transform.smoothscale(img, (largura, altura))

bg_escalado = escalar_fundo(bg_image, tela.get_size())

# =====================
# Gerenciador de telas
# =====================
class ScreenManager:
    def __init__(self):
        self.stack = []

    def push(self, screen):
        self.stack.append(screen)

    def pop(self):
        if self.stack:
            self.stack.pop()

    def current(self):
        return self.stack[-1] if self.stack else None

manager = ScreenManager()

# =====================
# Tela Menu Principal
# =====================
class TelaMenu:
    def __init__(self, surface):
        self.surface = surface
        self.titulo = 'Centro de Análises'

        self.botoes = [
            Botao('Análise de Planilha', self.go_planilha),
            Botao('Análise de Documentos', lambda: print('Análise de Documentos iniciada!')),
            Botao('Análise de Imagem', lambda: print('Análise de Imagem iniciada!')),
            Botao('Análise de Dados', lambda: print('Análise de Dados iniciada!')),
        ]
        self.recalcular_layout()

    def go_planilha(self):
        manager.push(TelaPlanilha(self.surface, on_voltar=manager.pop))

    def recalcular_layout(self):
        (self.card_rect, self.largura_botao, self.altura_botao,
         self.espacamento, self.padding_vertical,
         self.fonte_botoes, self.fonte_titulo) = calcular_layout(self.surface, len(self.botoes))

        # posiciona botões
        x = self.card_rect.x + (self.card_rect.w - self.largura_botao) // 2
        y = self.card_rect.y + self.padding_vertical
        for b in self.botoes:
            b.rect = pygame.Rect(x, y, self.largura_botao, self.altura_botao)
            y += self.altura_botao + self.espacamento

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.recalcular_layout()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for botao in self.botoes:
                botao.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for botao in self.botoes:
                if botao.pressed:
                    botao.pressed = False
                    botao.checar_clique(event.pos)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for botao in self.botoes:
            botao.atualizar_hover(mouse_pos)

    def draw(self):
        # fundo
        if bg_escalado is not None:
            self.surface.blit(bg_escalado, (0, 0))
        else:
            self.surface.fill(COR_FUNDO_BASE)

        draw_vignette(self.surface)

        # Card translúcido
        card_surf = pygame.Surface(self.card_rect.size, pygame.SRCALPHA)
        for i in range(self.card_rect.height):
            import components.ui_base as ui_base
            alpha = int(ui_base.lerp(90, 140, i / max(1, self.card_rect.height - 1)))
            pygame.draw.rect(card_surf, (255, 255, 255, alpha), (0, i, self.card_rect.width, 1))
        mask = pygame.Surface(self.card_rect.size, pygame.SRCALPHA)
        draw_rounded_rect(mask, mask.get_rect(), (255, 255, 255, 0), radius=24)
        card_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        draw_shadow(self.surface, self.card_rect, radius=28, offset=(0, 10), alpha=90)
        self.surface.blit(card_surf, self.card_rect)
        pygame.draw.rect(self.surface, ajustar_claridade(COR_DESTAQUE, 1.4), self.card_rect, width=2, border_radius=24)

        titulo_render = self.fonte_titulo.render(self.titulo, True, (255, 255, 255))
        self.surface.blit(
            titulo_render,
            (self.card_rect.centerx - titulo_render.get_width() // 2,
             self.card_rect.y - max(8, titulo_render.get_height()) - 8),
        )

        for botao in self.botoes:
            botao.desenhar(self.surface, self.fonte_botoes)

# =====================
# Loop principal
# =====================
clock = pygame.time.Clock()
manager.push(TelaMenu(tela))

rodando = True
while rodando:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        elif event.type == pygame.VIDEORESIZE:
            tela = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            bg_escalado = escalar_fundo(bg_image, (event.w, event.h))
        # repassa evento à tela ativa
        scr = manager.current()
        if scr:
            scr.handle_event(event)

    # atualiza e desenha tela ativa
    scr = manager.current()
    if scr:
        scr.update(dt)
        scr.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()
