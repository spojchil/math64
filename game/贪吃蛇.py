import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 游戏窗口尺寸
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("贪吃蛇游戏")

# 使用中文字体（确保系统存在该字体）
try:
    font = pygame.font.Font("simhei.ttf", 24)  # 使用黑体
except:
    font = pygame.font.SysFont("simhei", 24)  # 后备方案

# 蛇参数
SNAKE_SIZE = 20
SNAKE_SPEED = 15

clock = pygame.time.Clock()


def show_score(score):
    text = font.render("得分: " + str(score), True, WHITE)
    screen.blit(text, (10, 10))


def show_paused():
    text = font.render("游戏已暂停（按空格键继续）", True, WHITE)
    screen.blit(text, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 15))


def game_loop():
    game_over = False
    game_close = False
    paused = False  # 新增暂停状态

    # 初始位置和速度
    x = WINDOW_WIDTH // 2
    y = WINDOW_HEIGHT // 2
    dx = 0
    dy = 0

    snake_body = []
    snake_length = 1

    # 优化食物生成逻辑
    def generate_food():
        return (random.randrange(0, WINDOW_WIDTH - SNAKE_SIZE + 1, SNAKE_SIZE),
random.randrange(0, WINDOW_HEIGHT - SNAKE_SIZE + 1, SNAKE_SIZE)

                food_x, food_y = generate_food()

    while not game_over:
        # 处理事件（所有状态都需要响应退出事件）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # 空格键暂停
                    paused = not paused

                if not paused and not game_close:
                    if event.key == pygame.K_LEFT and dx != SNAKE_SIZE:
                        dx = -SNAKE_SIZE
                        dy = 0
                    elif event.key == pygame.K_RIGHT and dx != -SNAKE_SIZE:
                        dx = SNAKE_SIZE
                        dy = 0
                    elif event.key == pygame.K_UP and dy != SNAKE_SIZE:
                        dy = -SNAKE_SIZE
                        dx = 0
                    elif event.key == pygame.K_DOWN and dy != -SNAKE_SIZE:
                        dy = SNAKE_SIZE
                        dx = 0

        if game_close:
            screen.fill(BLACK)
            game_over_text = font.render("游戏结束！得分: " + str(snake_length - 1), True, RED)
            restart_text = font.render("按R重新开始 按Q退出", True, WHITE)
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 - 50))
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 10))
            pygame.display.update()

            # 处理结束状态输入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        game_loop()
            continue

        if paused:
            screen.fill(BLACK)
            show_paused()
            pygame.display.update()
            clock.tick(SNAKE_SPEED)
            continue

        # 边界检测
        if x >= WINDOW_WIDTH or x < 0 or y >= WINDOW_HEIGHT or y < 0:
            game_close = True

        # 更新位置
        x += dx
        y += dy

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [food_x, food_y, SNAKE_SIZE, SNAKE_SIZE])

        # 蛇身体处理
        snake_head = [x, y]
        snake_body.append(snake_head)

        if len(snake_body) > snake_length:
            del snake_body[0]

        # 自碰检测
        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_close = True

        # 绘制蛇身体
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE])

        # 吃食物检测
        if x == food_x and y == food_y:
            food_x, food_y = generate_food()
            snake_length += 1

        show_score(snake_length - 1)
        pygame.display.update()

        clock.tick(SNAKE_SPEED)


if __name__ == "__main__":
    game_loop()
    pygame.quit()