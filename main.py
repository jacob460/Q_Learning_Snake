import os.path
import random
import pickle
from snake_game import SnakeGame, Direction, Point, BLOCK_SIZE

MODEL = 'model.pickle'

def load_model():
    return pickle.load(open(MODEL, 'rb'))

class Agent:
    def __init__(self, learning_rate, discount_factor, exploration_rate, decay_rate):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.decay_rate = decay_rate
        self.episodes = []
        pass

    def save(self):
        with open(MODEL, 'wb') as output:
            pickle.dump(self, output)
        pass

    def choose_move(self, state, game):
        move_list = []
        rand = random.randint(0,2)
        
        if (state in self.q_table) and (random.uniform(0,1) > self.exploration_rate):
            optimal_move = max(self.q_table.get(state))
            for i, x in enumerate(self.q_table.get(state)):
                if x == optimal_move:
                    move_list.append(i)
            rand = random.choice(move_list)
            return game.options[rand]

        return game.options[rand]



    def update_qtable(self, current_state, action, reward, next_state, options):
        #Q(state,action) = Q(state, action) + learning_rate(immediate_reward + discount_factor*max(next_state, next_action) - Q(state, action))
       
        index = options.index(action)
        if not current_state in self.q_table:
            self.q_table[current_state] = [0,0,0]
        if next_state in self.q_table:
            self.q_table[current_state][index] = self.q_table[current_state][index] + self.learning_rate*(reward + self.discount_factor*max(self.q_table[next_state]) - self.q_table[current_state][index])
        else:
            self.q_table[next_state] = [0,0,0]
            self.q_table[current_state][index] = self.q_table[current_state][index] + self.learning_rate*(reward + self.discount_factor*max(self.q_table[next_state]) - self.q_table[current_state][index])
        
        if len(self.episodes)%100 == 0:
            self.exploration_rate = max(0.01, self.exploration_rate*self.decay_rate)
        pass

def state_builder(game):
    danger = [game.food.x-game.head.x, game.food.y-game.head.y , game.direction]

    for x in game.options:
        if x == Direction.LEFT:
            if game.head.x - BLOCK_SIZE < 0 or Point(game.head.x - BLOCK_SIZE, game.head.y) in game.snake[1:]:
                danger.append(True)
            else:
                danger.append(False)
        elif x == Direction.RIGHT:
            if game.head.x > game.w - 2*BLOCK_SIZE or Point(game.head.x + BLOCK_SIZE, game.head.y) in game.snake[1:]:
                danger.append(True)
            else:
                danger.append(False)
        elif x == Direction.UP:
            if game.head.y - BLOCK_SIZE < 0 or Point(game.head.x, game.head.y - BLOCK_SIZE) in game.snake[1:]:
                danger.append(True)
            else:
                danger.append(False)
        elif x == Direction.DOWN:
            if game.head.y > game.h - 2*BLOCK_SIZE or Point(game.head.x, game.head.y + BLOCK_SIZE) in game.snake[1:]:
                danger.append(True)
            else:
                danger.append(False)

    return tuple(danger)


if __name__ == '__main__':
    game = SnakeGame()
    max_score = 0
    if os.path.exists(MODEL):
        agent = load_model()
    else:
        #Agent(self, learning_rate, discount_factor, exploration_rate, decay_rate):
        agent = Agent(0.1, 0.95, 1, 0.995)
    #print(agent.q_table)
    #print('Beginning Q_table: ', len(agent.q_table))
    #print('Beginning episodes: ', len(agent.episodes))

    #while len(agent.episodes) < 100000:
    while True:
        # game loop
        num_moves = 0
        while True:

            current_state = state_builder(game)
            move = agent.choose_move(current_state, game)

            save_quit, game_over, score, food, head, direction, reward, options = game .play_step(move)

            agent.update_qtable(current_state, move, reward, state_builder(game), options)
            num_moves += 1
            if game_over:
                break
        agent.episodes.append([num_moves, score])
        max_score  = max(score, max_score)
        game = SnakeGame()
        if save_quit:
            break

    #print('Final Score', max_score)
    #print('Final Q_table: ', len(agent.q_table))
    #print('Final episodes: ', len(agent.episodes))

    agent.save()