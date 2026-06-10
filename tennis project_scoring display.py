import os  
import sys  
from campy.graphics.gwindow import GWindow
from campy.graphics.gobjects import GRect, GOval, GLabel, GArc  
from campy.gui.events.mouse import onmousemoved, onmouseclicked  
from campy.gui.events.timer import pause

# Game constants
WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 700

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_Y_OFFSET = 40

BALL_RADIUS = 10
BALL_DIAMETER = BALL_RADIUS * 2

# Brick constants
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_HEIGHT = 12
BRICK_SEP = 4  
BRICK_WIDTH = (WINDOW_WIDTH - (BRICK_COLS - 1) * BRICK_SEP) / BRICK_COLS
BRICK_Y_OFFSET = 60  

ROW_COLORS = ["red", "orange", "yellow", "green", "cyan"]
ROW_SCORES = [50, 40, 30, 20, 10]

SCORE_FILE = "high_scores.txt"
DELAY = 15 

def create_bricks(window):
    """Generates a grid of bricks and assigns unique score values directly to each."""
    bricks = []
    for row in range(BRICK_ROWS):
        color = ROW_COLORS[row % len(ROW_COLORS)]
        points_for_this_row = ROW_SCORES[row % len(ROW_SCORES)]
        brick_y = BRICK_Y_OFFSET + row * (BRICK_HEIGHT + BRICK_SEP)
        
        for col in range(BRICK_COLS):
            brick_x = col * (BRICK_WIDTH + BRICK_SEP)
            
            brick = GRect(BRICK_WIDTH, BRICK_HEIGHT, x=brick_x, y=brick_y)
            brick.filled = True
            brick.fill_color = color
            brick.score_value = points_for_this_row
            
            window.add(brick)
            bricks.append(brick)
    return bricks

def load_high_scores():
    """Reads the top 3 scores from a local file."""
    if not os.path.exists(SCORE_FILE):
        return [0, 0, 0]
    try:
        with open(SCORE_FILE, "r") as file:
            scores = []
            for line in file:
                cleaned_line = line.strip()
                if cleaned_line.isdigit():
                    scores.append(int(cleaned_line))
            scores.sort(reverse=True)
            while len(scores) < 3:
                scores.append(0)
            return scores[:3]
    except:
        return [0, 0, 0]

def save_high_scores(new_score):
    """Saves the top 3 scores to a file."""
    scores = load_high_scores()
    scores.append(new_score)
    scores.sort(reverse=True)
    top_3 = scores[:3]
    with open(SCORE_FILE, "w") as file:
        for s in top_3:
            file.write(f"{s}\n")
    return top_3

def draw_sad_face(window, top_scores):
    """Draws a clear arcade sad face with clean, structured text banners surrounding it."""
    center_x = WINDOW_WIDTH / 2
    center_y = WINDOW_HEIGHT / 2 + 20  
    
    # 1. "YOU LOSE!" Banner (Above the face)
    lose_label = GLabel("YOU LOSE!", x=center_x, y=center_y - 90)
    try:
        lose_label.font = "Arial-36-bold"  
    except:
        pass
    lose_label.color = "red"
    lose_label.x = center_x - (lose_label.width / 2 if lose_label.width else 95)
    window.add(lose_label)
    
    # 2. Head outline
    face_radius = 60
    face_bg = GOval(face_radius * 2, face_radius * 2, x=center_x - face_radius, y=center_y - face_radius)
    face_bg.filled = True
    face_bg.fill_color = "light gray"  
    face_bg.color = "dark red"        
    window.add(face_bg)
    
    # 3. Eyes
    left_eye = GOval(12, 12, x=center_x - 25, y=center_y - 20)
    left_eye.filled = True
    left_eye.fill_color = "dark red"
    window.add(left_eye)
    
    right_eye = GOval(12, 12, x=center_x + 13, y=center_y - 20)
    right_eye.filled = True
    right_eye.fill_color = "dark red"
    window.add(right_eye)
    
    # 4. Sad Mouth
    mouth = GArc(50, 40, 0, 180, x=center_x - 25, y=center_y + 10)
    mouth.color = "dark red"
    window.add(mouth)

    # 5. NEW: "Game Over! Click to Play Again." Banner (Just below the face)
    action_label = GLabel("Game Over! Click to Play Again.", x=center_x, y=center_y + 95)
    try:
        action_label.font = "Arial-16-bold"
    except:
        pass
    action_label.color = "black"
    action_label.x = center_x - (action_label.width / 2 if action_label.width else 115)
    window.add(action_label)

    # 6. NEW: High Scores Banner (Below the action prompt)
    scores_label = GLabel(f"Top 3 High Scores: {top_scores}", x=center_x, y=center_y + 125)
    try:
        scores_label.font = "Arial-14"
    except:
        pass
    scores_label.color = "gray"
    scores_label.x = center_x - (scores_label.width / 2 if scores_label.width else 100)
    window.add(scores_label)

def play_game(window):
    """Encapsulates a single round of breakout gameplay."""
    window.clear()
    
    # Setup Paddle
    paddle_x = (WINDOW_WIDTH - PADDLE_WIDTH) / 2
    paddle_y = WINDOW_HEIGHT - PADDLE_Y_OFFSET - PADDLE_HEIGHT
    paddle = GRect(PADDLE_WIDTH, PADDLE_HEIGHT, x=paddle_x, y=paddle_y)
    paddle.filled = True
    paddle.fill_color = "black"
    window.add(paddle)
    
    # Setup Ball
    ball_x = paddle_x + (PADDLE_WIDTH / 2) - BALL_RADIUS
    ball_y = paddle_y - BALL_DIAMETER
    ball = GOval(BALL_DIAMETER, BALL_DIAMETER, x=ball_x, y=ball_y)
    ball.filled = True
    ball.fill_color = "red"
    window.add(ball)

    # Generate Bricks
    bricks = create_bricks(window)

    # Setup On-Screen Score Display
    current_score = 0
    score_label = GLabel(f"Score: {current_score}", x=15, y=35)
    try:
        score_label.font = "Arial-20"
    except:
        pass 
    window.add(score_label)

    # Velocity values
    change_x = 3
    change_y = -3  

    # Paddle tracking
    def track_mouse(event):
        new_x = event.x - PADDLE_WIDTH / 2
        if new_x < 0:
            new_x = 0
        elif new_x > WINDOW_WIDTH - PADDLE_WIDTH:
            new_x = WINDOW_WIDTH - PADDLE_WIDTH
            
        if ball.y <= WINDOW_HEIGHT and bricks:
            paddle.x = new_x

    onmousemoved(track_mouse)

    # --- MAIN MATCH LOOP ---
    while True:
        ball.move(change_x, change_y)
        
        # Wall Collisions
        if ball.x <= 0 or ball.x + BALL_DIAMETER >= WINDOW_WIDTH:
            change_x = -change_x
            
        if ball.y <= 0:
            change_y = -change_y
            
        # Paddle Collision
        if change_y > 0:  
            if ball.y + BALL_DIAMETER >= paddle.y and ball.y + BALL_DIAMETER <= paddle.y + PADDLE_HEIGHT:
                if ball.x + BALL_DIAMETER >= paddle.x and ball.x <= paddle.x + PADDLE_WIDTH:
                    change_y = -change_y  
        
        # Brick Collision
        for brick in bricks[:]:
            if (ball.x + BALL_DIAMETER >= brick.x and ball.x <= brick.x + BRICK_WIDTH and
                ball.y + BALL_DIAMETER >= brick.y and ball.y <= brick.y + BRICK_HEIGHT):
                
                current_score += brick.score_value
                score_label.text = f"Score: {current_score}"
                window.remove(brick)
                bricks.remove(brick)
                change_y = -change_y  
                break  

        # Game Over Condition
        if ball.y > WINDOW_HEIGHT:
            top_scores = save_high_scores(current_score)
            draw_sad_face(window, top_scores)
            break  
            
        # Victory Condition
        if not bricks:
            top_scores = save_high_scores(current_score)
            score_label.text = f"Victory! Click to Play Again. Top 3: {top_scores}"
            break  

        pause(DELAY)

    # --- END GAME WAITING LOOP ---
    user_choice = {"action": None}

    def process_end_click(event):
        user_choice["action"] = "restart"

    onmouseclicked(process_end_click)

    while user_choice["action"] is None:
        pause(DELAY)

    return True

def main():
    window = GWindow(WINDOW_WIDTH, WINDOW_HEIGHT, title="Breakout Game")
    
    while True:
        should_continue = play_game(window)
        if not should_continue:
            break

if __name__ == '__main__':
    main()
