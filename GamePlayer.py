from abc import ABC, abstractmethod
import numpy as np
from typing import List, Optional
from enum import Enum
import random
#import pandas as pd
import signal

class timeout:
    def __init__(self, milliseconds=10, error_message='Timeout'):
        self.milliseconds = milliseconds / 1000.0
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.milliseconds, 1.0)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class GameAction(Enum):
    MEASURE = 'M'
    PAULIX = 'X'
    PAULIZ = 'Z'
    HADAMARD = 'H'
    REVERSE = 'R'

    def __str__(self) -> str:
        return str(self.value)


def ga_str(ga: GameAction) -> Optional[str]:
    if ga is None:
        return None
    return str(ga)

def hand_to_str(hand):
    hand_str = []
    for action in hand:
        hand_str.append(str(action))
    return hand_str

list_of_game_actions = [GameAction.MEASURE,GameAction.PAULIX,GameAction.PAULIZ,GameAction.HADAMARD,GameAction.REVERSE]
default_game_action_probabilities = [0.05,0.25,0.25,0.25,0.2]

class GameBot(ABC):
    '''
    Initialization
    '''
    def __init__(self,bot_name):
        self.bot_name = bot_name


    '''
    Implement these methods to create a game bot.  The player can have any state it wants.
    '''
    @abstractmethod
    def play_action(self,
                    team: int,
                    round_number: int,
                    hand: List[GameAction],
                    prev_turn: List) -> Optional[GameAction]:
        '''
        Takes the current state, the round number, the number of rounds in the game, and the order that
        this player is playing in this round.
        '''
        pass


def rotation_matrix(theta: float) -> np.array:
    return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]])

def measure(state: np.array) -> int:
    probability = state[0]**2
    #ensure it's between one and zero
    if probability < 0:
        probability = 0
    elif probability > 1:
        probability = 1

    basis_states = [np.array([1,0]),np.array([0,1])]

    outcome = np.random.choice([0, 1], p=[probability, 1 - probability])
    return basis_states[outcome]


class GamePlayer(ABC):
    def __init__(self,
                strategy_0: GameBot,
                strategy_1: GameBot,
                 num_rounds: int = 100,
                 budget: int  = 20,
                 hand_size: int  = 5,
                 theta: float = 2*np.pi/100.0,
                 game_action_probabilities: List = default_game_action_probabilities):
        self.num_rounds = num_rounds
        self.round_number = 0
        self.state = np.array([np.sqrt(0.5), np.sqrt(0.5)])
        self.strategies = [strategy_0,strategy_1]
        self.actions_dealt = [0,0]
        self.actions_budget = budget
        self.prev_actions = [None,None]
        self.prev_outcomes = [None,None]
        self.hand_size = hand_size
        self.theta = theta
        self.direction = 1
        self.hands = [[],[]]
        self.game_action_probabilities = game_action_probabilities

        self.log = "Team |0> is " + self.strategies[0].bot_name + "\n"
        self.log += "Team |1> is " + self.strategies[1].bot_name + "\n"
        self.log += "======================================\n"

        self.deal_initial_actions()

        self.log += "======================================\n"



    def deal_initial_actions(self):
        '''
        Deal the initial hands
        '''
        for j in range(self.hand_size):
            self.deal_card(0)
            self.deal_card(1)


    def deal_card(self,team):
        '''
        Give team a new action and add it to their hand
        '''

        #check whether their hand is fulltext
        if len(self.hands[team]) >= self.hand_size:
            return None

        #deal cards with different probabilities
        action = np.random.choice(list_of_game_actions,p=self.game_action_probabilities)
        self.hands[team].append(action)
        self.actions_dealt[team] += 1

        self.log += "\t Team |" + str(team) + "> added " + str(action) + " to their hand (%d/%d)" % (self.actions_dealt[team],self.actions_budget) + "\n"

        return action

    def randomly_deal_card(self,team):
        p = self.actions_budget/float(self.num_rounds)

        if np.random.random() < p and self.actions_dealt[team] < self.actions_budget:
            return self.deal_card(team)

        return None

    def take_action(self, action: GameAction):
        '''
        Take an action on a state (and report the result of a measurement to a strategy if it measured).
        '''
        if action == GameAction.MEASURE:
            self.state = measure(self.state)
            self.log += "\t State collapsed to " + str(self.state.tolist()) + "\n"

        elif action == GameAction.PAULIX:
            X = np.array([[0, 1], [1, 0]])
            self.state = np.dot(X, self.state)
        elif action == GameAction.PAULIZ:
            Z = np.array([[1, 0], [0, -1]])
            self.state = np.dot(Z, self.state)
        elif action == GameAction.HADAMARD:
            H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
            self.state = np.dot(H, self.state)
        elif action == GameAction.REVERSE:
            self.direction = -1 * self.direction

    def play_round_team(self,team,prev_turn):
        try:
            with timeout():
                action = self.strategies[team].play_action(team,self.round_number,self.hands[team],prev_turn)
        except TimeoutError:
            self.log += "\t Team |" + str(team) + "> timed out\n"
            action = None
        except Exception as e:
            self.log += "\t Team |" + str(team) + "> had an unexpected error: " + str(e) + "\n"
            action = None

        #check the action is valid
        if action is not None and action not in self.hands[team]:
            print("Round %d: Team |%d> tried to play an action they don't have: %s" %(self.round_number,team,action))
            action = None

        if action is not None:
            self.log += "\t Team |" + str(team) + "> plays " + str(action) + "\n"
            self.take_action(action)
            self.hands[team].remove(action)

        self.prev_actions[team] = action
        if action is GameAction.MEASURE:
            self.prev_outcomes[team] = np.copy(self.state).tolist()
        else:
            self.prev_outcomes[team] = None


    def play_round(self):

        prev_turn = {'team0_action':self.prev_actions[0], \
                     'team1_action':self.prev_actions[1], \
                     'team0_measurement':self.prev_outcomes[0], \
                     'team1_measurement':self.prev_outcomes[1]}


        self.play_round_team(0,prev_turn)

        prev_turn = {'team0_action':self.prev_actions[0], \
                     'team1_action':self.prev_actions[1], \
                     'team0_measurement':self.prev_outcomes[0], \
                     'team1_measurement':self.prev_outcomes[1]}

        self.play_round_team(1,prev_turn)

        #randomly chose whether each team gets a hand dealt
        team0_new_card = self.randomly_deal_card(0)
        team1_new_card = self.randomly_deal_card(1)

        self.round_number += 1
        rotate = rotation_matrix(self.direction*self.theta)
        self.state = np.dot(rotate, self.state)


    def play_overtime(self,overtime_rounds,who_goes_last):

        for r in range(overtime_rounds):
            self.log += "Round " + str(self.round_number) + ". "
            self.log += "State: [%.3f,%.3f]\n" % (round(self.state[0],3),round(self.state[1],3))

            prev_turn = {'team0_action':self.prev_actions[0], \
                         'team1_action':self.prev_actions[1], \
                         'team0_measurement':self.prev_outcomes[0], \
                         'team1_measurement':self.prev_outcomes[1]}


            self.play_round_team(0,prev_turn)

            prev_turn = {'team0_action':self.prev_actions[0], \
                         'team1_action':self.prev_actions[1], \
                         'team0_measurement':self.prev_outcomes[0], \
                         'team1_measurement':self.prev_outcomes[1]}


            if r < overtime_rounds - 1:
                self.play_round_team(1,prev_turn)
            elif r == overtime_rounds - 1 and who_goes_last == 1:
                self.play_round_team(1,prev_turn)

            self.round_number += 1
            rotate = rotation_matrix(self.direction*self.theta)
            self.state = np.dot(rotate, self.state)


    def play_rounds(self):

        for r in range(self.num_rounds):
            self.log += "Round " + str(self.round_number) + ". "
            self.log += "State: [%.3f,%.3f]\n" % (round(self.state[0],3),round(self.state[1],3))

            self.play_round()

        #enter overtime

        #randomly a number of rounds
        overtime_rounds = np.random.randint(1 + (self.num_rounds/10))
        who_goes_last = np.random.randint(2)

        self.log += "--------Entering Overtime for %d extra rounds, and Team |%d> goes last--------\n" % (overtime_rounds,who_goes_last)

        self.play_overtime(overtime_rounds,who_goes_last)


        winning_state = self.declare_winner()
        if winning_state[0] == 1:
            self.log += "\nTeam |0>, " + self.strategies[0].bot_name + ", wins!\n"
        else:
            self.log += "\nTeam |1>, " + self.strategies[1].bot_name + ", wins!\n"

        return winning_state


    def get_event_log(self):
        return self.log

    def declare_winner(self):
        self.state = measure(self.state)
        self.log += "\t State collapsed to " + str(self.state.tolist()) + "\n"
        return self.state
