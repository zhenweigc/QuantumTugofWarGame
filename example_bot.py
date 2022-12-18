from typing import List, Optional
import numpy as np
import random
from GamePlayer import *

'''
Insert high-level explanation of your strategy here. Why did you design this strategy?
When should it work well, and when should it have trouble?
'''
class MyStrategy(GameBot):

    '''
        Initialize your bot here. The init function must take in a bot_name.
        You can use this to initialize any variables or data structures
        to keep track of things in the game
    '''
    win_threshold = 0.8

    cur_direction = None
    cur_state = None

    num_received = 0
    num_cards = 0

    theta = 2*np.pi/100.0

    epsilon = 0.001

    difference_threshold = 0.1

    # used for pre stage
    play_interval_count = 0

    def __init__(self,bot_name):
        self.bot_name = bot_name        #do not remove this

        #Initialize rotation direction and state
        self.cur_direction = 1
        self.cur_state = [1 / np.sqrt(2), 1 / np.sqrt(2)]

    def play_action(self,
                    team: int,
                    round_number: int,
                    hand: List[GameAction],
                    prev_turn: List) -> Optional[GameAction]:

        ##### IMPLEMENT AWESOME STRATEGY HERE ##################

        self.play_interval_count += 1
        self.calculate_state(round_number, team, prev_turn)

        if len(hand) > self.num_cards:
            self.num_received += len(hand) - self.num_cards
            self.num_cards = len(hand)

        opponent = None
        if team == 0:
            opponent = 1
        else:
            opponent = 0

        if round_number == 0:
            if team == 0:
                if GameAction.HADAMARD in hand and self.H_good(team):
                    self.num_cards -= 1
                    return GameAction.HADAMARD

        # before round 99
        if round_number < 99:
            if GameAction.MEASURE in hand:
                self.num_cards -= 1
                return GameAction.MEASURE

            # if we get R and Z, then out
            if self.play_interval_count >= 12 or round_number >= 90: # play time
                if self.rotate(team) and GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    self.play_interval_count = 0
                    return GameAction.REVERSE
                elif self.Z_Good(team) and GameAction.PAULIZ in hand:
                    self.num_cards -= 1
                    self.play_interval_count = 0
                    return GameAction.PAULIZ

            # adjust cards
            if self.num_received < 20 and len(hand) == 5:
                if GameAction.HADAMARD in hand and self.H_good(team):
                    self.num_cards -= 1
                    return GameAction.HADAMARD

                # make sure at lease 4 X cards
                if hand.count(GameAction.PAULIX) <= 4:
                    for card in hand:
                        if GameAction.REVERSE in hand:
                            self.num_cards -= 1
                            self.play_interval_count = 0
                            return GameAction.REVERSE
                        elif GameAction.PAULIZ in hand:
                            self.num_cards -= 1
                            self.play_interval_count = 0
                            return GameAction.PAULIZ
                        elif self.num_received < 19 and (hand.count(GameAction.HADAMARD) == 1 and round_number <= 80) or (hand.count(GameAction.HADAMARD) >= 2):
                                self.num_cards -= 1
                                return GameAction.HADAMARD

            return None

        if round_number >= 99:
            if np.absolute(self.cur_state[team]) > self.win_threshold:
                return None

            elif np.absolute(self.cur_state[opponent]) > np.absolute(self.cur_state[team]):
                if GameAction.PAULIX in hand:
                    self.num_cards -= 1
                    return GameAction.PAULIX
                if GameAction.HADAMARD in hand and self.H_good(team):
                    self.num_cards -= 1
                    return GameAction.HADAMARD

            if GameAction.REVERSE in hand and self.rotate(team):
                self.num_cards -= 1
                return GameAction.REVERSE

            if GameAction.PAULIZ in hand and self.Z_Good(team):
                self.num_cards -= 1
                return GameAction.PAULIZ

            if GameAction.MEASURE in hand:
                self.num_cards -= 1
                return GameAction.MEASURE

            return None

        #######################################################
        return None

    def calculate_state(self, round_number, team, prev_turn):
        '''
        if (round_number == 0):
            return;
        '''
        action_1 = prev_turn['team0_action']
        action_2 = prev_turn['team1_action']

        if (team == 0):
            if action_1 == GameAction.MEASURE:
                self.cur_state = prev_turn['team0_measurement']

            elif action_1 == GameAction.PAULIX:
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_1 == GameAction.PAULIZ:
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_1 == GameAction.HADAMARD:
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_1 == GameAction.REVERSE:
                self.cur_direction *= -1


            if action_2 == GameAction.MEASURE:
                self.cur_state = prev_turn['team1_measurement']

            elif action_2 == GameAction.PAULIX:
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_2 == GameAction.PAULIZ:
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_2 == GameAction.HADAMARD:
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_2 == GameAction.REVERSE:
                self.cur_direction *= -1


            #Rotate
            rotate = self.rotation_matrix(self.cur_direction*self.theta)
            self.cur_state = np.dot(rotate, self.cur_state)
            return;
        else:
            if action_2 == GameAction.MEASURE:
                self.cur_state = prev_turn['team1_measurement']

            elif action_2 == GameAction.PAULIX:
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_2 == GameAction.PAULIZ:
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_2 == GameAction.HADAMARD:
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_2 == GameAction.REVERSE:
                self.cur_direction *= -1

            #Rotate
            rotate = self.rotation_matrix(self.cur_direction*self.theta)
            self.cur_state = np.dot(rotate, self.cur_state)

            if action_1 == GameAction.MEASURE:
                self.cur_state = prev_turn['team0_measurement']

            elif action_1 == GameAction.PAULIX:
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_1 == GameAction.PAULIZ:
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_1 == GameAction.HADAMARD:
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_1 == GameAction.REVERSE:
                self.cur_direction *= -1

            return;

    def rotate(self, team) -> bool:
        temp_state = self.cur_state;
        tmp = rotation_matrix(self.cur_direction * self.theta);
        aftermath = np.dot(tmp, self.cur_state);

        tmp2 = rotation_matrix(-1 * self.cur_direction * self.theta);
        aftermath2 = np.dot(tmp2, self.cur_state);

        if np.absolute(aftermath[team]) < np.absolute(aftermath2[team]):
            return True;
        else:
            return False;


    #Check if using a Z-gate is useful
    def Z_Good(self, team) -> bool:
        temp_state = self.cur_state;
        tmp = rotation_matrix(self.cur_direction * self.theta);
        aftermath = np.dot(tmp, temp_state);


        Z = np.array([[1, 0], [0, -1]]);
        temp_state = np.dot(Z, temp_state);
        aftermath2 = np.dot(tmp, temp_state);

        if np.absolute(aftermath[team]) < np.absolute(aftermath2[team]):
            return True;
        else:
            return False;


    #Check if using a H-gate is useful
    def H_good(self, team) -> bool:
        temp_state = self.cur_state;
        temp_rt = rotation_matrix(self.cur_direction * self.theta);
        temp_me = np.absolute(np.dot(temp_rt, temp_state)[team]);

        H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
        temp_state = np.dot(temp_rt, np.dot(H, temp_state));

        if (temp_me < np.absolute(temp_state[team])):
            return True;
        else:
            return False;

    def rotation_matrix(self, theta) -> np.array:
        return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]])

