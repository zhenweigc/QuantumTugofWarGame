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

        # print(round_number)
        # print(hand)

        self.calculate_state(round_number, team, prev_turn)


        self.play_interval_count += 1

        # print(self.cur_state)
        #Verifying if the calculation is correct.
        # print(f'By calculation, current state is {self.cur_state}, round number is {round_number}.');
        #print(self.cur_state)


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
        if round_number < 95:
            # if we get R and Z, then out
            if self.play_interval_count >= 20 or round_number >= 90: # play time
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

                # make sure at lease 3 X cards, and no more than 1 MEASURE
                if hand.count(GameAction.PAULIX) < 3:
                    if hand.count(GameAction.MEASURE) >= 2:
                        self.num_cards -= 1
                        return GameAction.MEASURE

                    for card in hand:
                        if card != GameAction.PAULIX and card != GameAction.MEASURE:
                                self.num_cards -= 1
                                return card


                # for card in hand:
                #     if card != GameAction.PAULIX and card != GameAction.MEASURE:
                #         if card != GameAction.HADAMARD or self.H_good(team):
                #             self.num_cards -= 1
                #             return card

            return None

        # before final
        if round_number >= 95 and round_number < 99:
            if np.absolute(self.cur_state[opponent]) > self.win_threshold:
                if GameAction.HADAMARD in hand and self.H_good(team):
                    self.num_cards -= 1
                    return GameAction.HADAMARD
                elif hand.count(GameAction.PAULIX) >=4:
                    self.num_cards -= 1
                    return GameAction.PAULIX

            return None

        # final: keep as much as 3 X: X X X H R
        # if round_number == 99:
        #     if np.absolute(self.cur_state[opponent]) < np.absolute(self.cur_state[team]):
        #         if GameAction.MEASURE in hand:
        #             self.num_cards -= 1
        #             return GameAction.MEASURE
        #         elif GameAction.PAULIX in hand:
        #             self.num_cards -= 1
        #             return GameAction.PAULIX
        #     else:
        #         if GameAction.PAULIX in hand:
        #             self.num_cards -= 1
        #             return GameAction.PAULIX

        if round_number >= 99:
            # print(round_number)
            # print(self.cur_state[team])
            # print("Team: ", team)
            # print("Opponent: ", opponent)
            # # print("Opponent state: ", np.absolute(self.cur_state[opponent]))
            # print("Opponent state: ", self.cur_state[opponent])
            # print(hand)

            # can not believe a team has more than 3 X cards
            if GameAction.PAULIX in hand and round_number <= 101:
                self.num_cards -= 1
                return GameAction.PAULIX

            # if np.absolute(self.cur_state[team]) > self.win_threshold:
            if GameAction.MEASURE in hand and np.absolute(self.cur_state[team]) > self.win_threshold:
                self.num_cards -= 1
                return GameAction.MEASURE
            # return None

            if GameAction.HADAMARD in hand and self.H_good(team):
                self.num_cards -= 1
                return GameAction.HADAMARD

            # if np.absolute(self.cur_state[team]) - np.absolute(self.cur_state[opponent]) <= self.difference_threshold:
            if GameAction.REVERSE in hand and self.rotate(team):
                self.num_cards -= 1
                return GameAction.REVERSE

            if GameAction.PAULIZ in hand and self.Z_Good(team):
                self.num_cards -= 1
                return GameAction.PAULIZ

            # if np.absolute(self.cur_state[opponent]) > np.absolute(self.cur_state[team]):
            # if GameAction.PAULIX in hand:
            #     self.num_cards -= 1
            #     return GameAction.PAULIX

            # if GameAction.REVERSE in hand and self.rotate(team) :
            #     self.num_cards -= 1
            #     return GameAction.REVERSE

            # if GameAction.PAULIZ in hand and self.Z_Good(team):
            #     self.num_cards -= 1
            #     return GameAction.PAULIZ

            return None

        #######################################################
        return None

    def calculate_state(self, round_number, team, prev_turn):
        action_1 = prev_turn['team0_action']
        action_2 = prev_turn['team1_action']

        if (team == 0):
            #Apply previous actions for team 0
            if action_1 == GameAction.MEASURE:
                #print("1")
                self.cur_state = prev_turn['team0_measurement']

            elif action_1 == GameAction.PAULIX:
                #print("2")
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_1 == GameAction.PAULIZ:
                #print("3")
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_1 == GameAction.HADAMARD:
                #print("4")
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_1 == GameAction.REVERSE:
                #print("5")
                self.cur_direction *= -1


            #Apply previous actions for team 1
            if action_2 == GameAction.MEASURE:
                #print("1")
                self.cur_state = prev_turn['team1_measurement']

            elif action_2 == GameAction.PAULIX:
                #print("2")
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_2 == GameAction.PAULIZ:
                #print("3")
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_2 == GameAction.HADAMARD:
                #print("4")
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_2 == GameAction.REVERSE:
                #print("5")
                self.cur_direction *= -1


            #Rotate
            if (round_number > 0):
                rotate = self.rotation_matrix(self.cur_direction*self.theta)
                #print(self.cur_direction)
                #print(self.cur_state)
                self.cur_state = np.dot(rotate, self.cur_state)
                #print(self.cur_state)
        else:
            #Apply previous action from team 1
            if action_2 == GameAction.MEASURE:
                #print("1")
                self.cur_state = prev_turn['team1_measurement']

            elif action_2 == GameAction.PAULIX:
                #print("2")
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_2 == GameAction.PAULIZ:
                #rint("3")
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_2 == GameAction.HADAMARD:
                #print("4")
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_2 == GameAction.REVERSE:
                #print("5")
                self.cur_direction *= -1

            #Rotate
            if (round_number > 0):
                rotate = self.rotation_matrix(self.cur_direction*self.theta)
                #print(self.cur_direction)
                #print(self.cur_state)
                self.cur_state = np.dot(rotate, self.cur_state)
                #print(self.cur_state)

            #print(self.cur_state)
            #Apply previous action from team 0
            if action_1 == GameAction.MEASURE:
                #print("1")
                self.cur_state = prev_turn['team0_measurement']

            elif action_1 == GameAction.PAULIX:
                #print("2")
                X = np.array([[0, 1], [1, 0]])
                self.cur_state = np.dot(X, self.cur_state)

            elif action_1 == GameAction.PAULIZ:
                #print("3")
                Z = np.array([[1, 0], [0, -1]])
                self.cur_state = np.dot(Z, self.cur_state)

            elif action_1 == GameAction.HADAMARD:
                #print("4")
                H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]])
                self.cur_state = np.dot(H, self.cur_state)

            elif action_1 == GameAction.REVERSE:
                #print("5")
                self.cur_direction *= -1


    def rotate(self, team) -> bool:
        # if np.absolute(self.cur_state[team]) >= self.win_threshold and hand.count(GameAction.REVERSE) < 2:
        # if np.absolute(self.cur_state[team]) >= self.win_threshold:
        #     return False

        temp_state = self.cur_state;
        tmp = rotation_matrix(self.cur_direction * self.theta);
        aftermath = np.dot(tmp, self.cur_state);

        tmp2 = rotation_matrix(-1 * self.cur_direction * self.theta);
        aftermath2 = np.dot(tmp2, self.cur_state);

        if np.absolute(aftermath[team]) < np.absolute(aftermath2[team]):
            return True;
        else:
            return False;

    def rotate2(self, team):
        if self.cur_state[0] > 0 and self.cur_state[1] > 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return False
                else:
                    #Actuall, we got to make sure we don't over-rotate.
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
                else:
                    return False
        if self.cur_state[0] < 0 and self.cur_state[1] > 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
                else:
                    return False
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return False
                else:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
        if self.cur_state[0] < 0 and self.cur_state[1] < 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return False
                else:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
                else:
                    return False
        if self.cur_state[0] > 0 and self.cur_state[1] < 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;
                else:
                    return False
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return False
                else:
                    tmp = self.rotation_matrix(self.cur_direction * self.theta);
                    aftermath = np.dot(tmp, self.cur_state);
                    if np.absolute(aftermath[team]) < np.absolute(self.cur_state[team]):
                        return False;
                    else:
                        return True;

    #Check if using a Z-gate is useful

    def Z_Good(self, team) -> bool:
        # if np.absolute(self.cur_state[team]) >= self.win_threshold:
        #     return False

        temp_state = self.cur_state;
        #Compute no action & after rotation state
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
