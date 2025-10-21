import pygame

# =====================
# Tema / Cores
# =====================
COR_FUNDO_BASE = (255, 255, 255)      # branco
COR_DESTAQUE = (87, 11, 98)           # #570b62 (roxo)
COR_TEXTO = (87, 11, 98)
COR_TEXTO_INVERSO = (255, 255, 255)

def ajustar_claridade(rgb, fator=1.2):
    r, g, b = rgb
    return (min(int(r * fator), 255), min(int(g * fator), 255), min(int(b * fator), 255))

def lerp(a, b, t): return a + (b - a) * t
def lerp_color(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))

def draw_rounded_rect(surface, rect, color, radius=16, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)

def draw_shadow(surface, rect, radius=18, offset=(0, 6), alpha=60):
    shadow_surf = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), shadow_surf.get_rect(), border_radius=radius+8)
    surface.blit(shadow_surf, (rect.x - 20 + offset[0], rect.y - 20 + offset[1]))

def draw_vignette(surface):
    w, h = surface.get_size()
    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(40):
        alpha = int(80 * (i / 40))
        pygame.draw.rect(
            vignette, (0, 0, 0, alpha//6),
            pygame.Rect(i, i, w - 2*i, h - 2*i),
            width=1,
            border_radius=max(6, int(min(w, h) * 0.02))
        )
    surface.blit(vignette, (0, 0))

# =====================
# Botão com animação
# =====================
class Botao:
    def __init__(self, texto, acao):
        self.texto = texto
        self.acao = acao
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False
        self.pressed = False
        self.hover_t = 0.0  # 0 -> normal, 1 -> destaque

    def desenhar(self, superficie, fonte):
        alvo = 1.0 if self.hover else 0.0
        self.hover_t = lerp(self.hover_t, alvo, 0.18)
        cor_fundo = lerp_color(COR_FUNDO_BASE, COR_DESTAQUE, self.hover_t)
        cor_borda = lerp_color(COR_DESTAQUE, ajustar_claridade(COR_DESTAQUE, 1.4), self.hover_t)
        cor_texto = lerp_color(COR_TEXTO, COR_TEXTO_INVERSO, self.hover_t)

        scale = 0.98 if self.pressed else 1.0
        scaled_rect = self.rect.inflate(int(self.rect.w*(scale-1)), int(self.rect.h*(scale-1)))

        draw_shadow(superficie, scaled_rect, offset=(0, 8), alpha=70)
        draw_rounded_rect(superficie, scaled_rect, cor_fundo, radius=18)
        pygame.draw.rect(superficie, cor_borda, scaled_rect, width=2, border_radius=18)

        texto_render = fonte.render(self.texto, True, cor_texto)
        superficie.blit(
            texto_render,
            (scaled_rect.centerx - texto_render.get_width() // 2,
             scaled_rect.centery - texto_render.get_height() // 2),
        )

    def checar_clique(self, pos):
        if self.rect.collidepoint(pos):
            self.acao()

    def atualizar_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# =====================
# Layout responsivo + card translúcido
# =====================
def calcular_layout(superficie, n_botoes):
    largura, altura = superficie.get_size()
    largura_card = int(min(560, max(360, largura * 0.78)))
    largura_botao = int(largura_card * 0.88)
    altura_botao = max(52, int(altura * 0.09))
    espacamento = max(14, int(altura * 0.03))

    total_altura_botoes = n_botoes * altura_botao + max(0, (n_botoes - 1)) * espacamento
    padding_vertical = max(24, int(altura * 0.04))
    altura_card = total_altura_botoes + padding_vertical * 2

    x_card = (largura - largura_card) // 2
    y_card = (altura - altura_card) // 2
    card_rect = pygame.Rect(x_card, y_card, largura_card, altura_card)

    tamanho_fonte = max(18, int(altura_botao * 0.44))
    fonte_botoes = pygame.font.SysFont('Arial', tamanho_fonte, bold=True)
    fonte_titulo = pygame.font.SysFont('Arial', max(22, int(altura * 0.05)), bold=True)

    return card_rect, largura_botao, altura_botao, espacamento, padding_vertical, fonte_botoes, fonte_titulo
