from client.pynel.settings import pygame, pad_mod, WIDTH, BLACK, HEIGHT_SUR, HEIGHT, HEIGHT_MENU
from client.pynel.helpers import draw_text, text_width
from client.pynel.modules.hd import HdModule
from client.pynel.modules.cpu import CpuModule
from client.pynel.modules.memory import MemoryModule
from client.pynel.modules.ip import IpModule
from client.pynel.modules.processo import ProcessModule
from client.pynel.connect import SOCKET_ABERTOS


# corrige o erro de abrir duas vezes
if __name__ != "__main__":
    exit()


clock = pygame.time.Clock()
fim = False

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
menu_sur = pygame.surface.Surface((WIDTH, HEIGHT_SUR))

geral = True
pintar_count = 0

# menu sel sera iniciado em 0
primeira_tecla = True
menu_sel = 0

menus = [
    CpuModule(),
    MemoryModule(),
    HdModule(),
    IpModule(),
    ProcessModule()
]


def draw_menu():
    menu_sur.fill(BLACK)

    pygame.draw.rect(menu_sur, (255, 255, 255), (0, 0, WIDTH, .5))

    for idx, menu in enumerate(menus):
        sector = WIDTH // len(menus)
        draw_text(menu_sur, menu.nome, 3, x=sector * idx + WIDTH // (len(menus) * 2) - text_width(menu.nome) / 2)
        if menu_sel == idx and not geral:
            pygame.draw.rect(menu_sur, (255, 0, 0), (sector * idx, HEIGHT_MENU - 3, sector, 3))

    if geral:
        pygame.draw.rect(menu_sur, (255, 0, 0), (0, HEIGHT_MENU - 3, WIDTH, 3))

    DISPLAY.blit(menu_sur, (0, HEIGHT_SUR))


def update_menu_sel(eventos):
    if geral:
        for menu in menus:
            menu.update_geral(eventos)
    else:
        menus[menu_sel].update(eventos)


def draw_menu_sel():
    if geral:
        draw_geral()
    else:
        menus[menu_sel].sur.fill(BLACK)
        menus[menu_sel].use_init_height(True)

        if menus[menu_sel].use_draw_tick:
            menus[menu_sel].draw_tick()
        else:
            menus[menu_sel].draw()

        DISPLAY.blit(menus[menu_sel].sur, (0, 0))


def draw_geral():
    # soma de todos os indexes para agir como uma surface só
    index_off = 1

    draw_text(DISPLAY, "Visão Geral (SPACE Para sair da visão geral  |  <- -> Para navegar)", 10)

    for menu in menus:
        menu.sur.fill(BLACK)
        menu.use_init_height(False)
        menu.draw_geral()
        DISPLAY.blit(menu.sur, (0, index_off * (pad_mod + 10)))
        index_off += menu.index


while not fim:
    # resetar os indexes para não acumular infinitamente no loop
    for men in menus:
        men.index = 0

    # configurando o clock para 30 vezes por segundo
    clock.tick(30)

    # pega os eventos
    eventos = pygame.event.get()

    # roda a cada tick
    menus[menu_sel].update_tick(eventos)

    if menus[menu_sel].use_draw_tick and not geral:
        DISPLAY.fill(BLACK)
        draw_menu_sel()

    # pintando as surfaces somente quando o count for <= zero
    if pintar_count <= 0:
        # update o menu
        update_menu_sel(eventos)

        if not menus[menu_sel].use_draw_tick:
            DISPLAY.fill(BLACK)
            draw_menu_sel()

    draw_menu()

    pygame.display.update()

    for event in eventos:
        if event.type == pygame.QUIT:
            pygame.quit()
            fim = True

            for menu in menus:
                menu.dispose()

            for socket in SOCKET_ABERTOS:
                socket.close()

            exit(0)
            break

        if event.type == pygame.KEYDOWN:
            pintar_count = -3

            if event.key == pygame.K_RIGHT:
                menus[menu_sel].menu_sel = False
                geral = False

                menu_sel += 1

                if menu_sel >= len(menus):
                    menu_sel = 0

                if not primeira_tecla:
                    menus[menu_sel].menu_sel = True

            if event.key == pygame.K_LEFT:
                menus[menu_sel].menu_sel = False

                geral = False
                menu_sel -= 1

                if menu_sel < 0:
                    menu_sel = len(menus) - 1

                if not primeira_tecla:
                    menus[menu_sel].menu_sel = True

            if event.key == pygame.K_SPACE:
                geral = not geral

            if primeira_tecla:
                menu_sel = 0
                primeira_tecla = False
                menus[menu_sel].menu_sel = True

    # incrementa o clock
    pintar_count += 1

    # faz com que as surfaces sejam pintadas duas vezes por segundo
    if pintar_count >= 15:
        pintar_count = 0

