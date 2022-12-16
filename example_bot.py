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
    win_threshold = 0.9
    
    cur_direction = None
    cur_state = None
    
    num_received = 0
    num_cards = 0
    
    theta = 2*np.pi/100.0
    
    epsilon = 0.001
    
    difference_threshold = 0.1
    
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
        #print(round_number)
        #print(self.cur_state)
        #print(hand)
        if (round_number > 0):
            self.calculate_state(prev_turn)
        
        
        if len(hand) > self.num_cards:
            self.num_received += len(hand) - self.num_cards
            self.num_cards = len(hand)
        
        opponent = None
        if team == 0:
            opponent = 1
        else:
            opponent = 0
        
        if round_number >= 99:
            #print(round_number)
            #print(self.cur_state[team])
            if np.absolute(self.cur_state[team]) > self.win_threshold:
                return None
            
            elif np.absolute(self.cur_state[opponent]) > self.win_threshold:
                #print("2")
                if GameAction.PAULIX in hand:
                    self.num_cards -= 1
                    return GameAction.PAULIX
                
                if GameAction.HADAMARD in hand:
                    self.num_cards -= 1
                    return GameAction.HADAMARD
                
                #if GameAction.PAULIZ in hand:
                    #self.num_cards -= 1
                    #return GameAction.PAULIZ
                
                
                if self.rotate(team) and GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    return GameAction.REVERSE
                
                
            elif np.absolute(self.cur_state[team] - self.cur_state[opponent]) <= self.difference_threshold:
                 if self.rotate(team) and GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    return GameAction.REVERSE
                
            elif np.absolute(self.cur_state[team]) > np.absolute(self.cur_state[opponent]):
                #print("3")
                if self.rotate(team) and GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    return GameAction.REVERSE

            elif np.absolute(self.cur_state[opponent]) > np.absolute(self.cur_state[team]): 
                #print("4")
                #print(hand)
                if GameAction.PAULIX in hand:
                    self.num_cards -= 1
                    return GameAction.PAULIX
                
                if GameAction.HADAMARD in hand:
                    self.num_cards -= 1
                    return GameAction.HADAMARD
                
                if self.rotate(team) and GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    return GameAction.REVERSE
                
        else:
            #print(round_number)
            if self.num_received < 20 and len(hand) == 5:
                if GameAction.MEASURE in hand:
                    self.num_cards -= 1
                    return GameAction.MEASURE
                
                if GameAction.PAULIZ in hand:
                    self.num_cards -= 1
                    return GameAction.PAULIZ
                
                if GameAction.REVERSE in hand:
                    self.num_cards -= 1
                    return GameAction.REVERSE
                
                #if GameAction.HADAMARD in hand:
                    #self.num_cards -= 1
                    #return GameAction.HADAMARD
        
        
        #######################################################
        return None
    
    def calculate_state(self, prev_turn):
        action_1 = prev_turn['team0_action']
        action_2 = prev_turn['team1_action']
        
        #print(action_1)
        #print(action_2)
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
        
        rotate = self.rotation_matrix(self.cur_direction*self.theta)
        #print(self.cur_direction)
        #print(self.cur_state)
        self.cur_state = np.dot(rotate, self.cur_state)
        #print(self.cur_state)
    
    def rotate(self, team):
        if self.cur_state[0] > 0 and self.cur_state[1] > 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return False
                else:
                    return True
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return True
                else:
                    return False
        if self.cur_state[0] < 0 and self.cur_state[1] > 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return True
                else:
                    return False
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return False
                else:
                    return True
        if self.cur_state[0] < 0 and self.cur_state[1] < 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return False
                else:
                    return True
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return True
                else:
                    return False
        if self.cur_state[0] > 0 and self.cur_state[1] < 0:
            if team == 0:
                #Move to the direction of 0
                if self.cur_direction == 1:
                    return True
                else:
                    return False
            else:
                #Move to the direction of 1
                if self.cur_direction == 1:
                    return False
                else:
                    return True
    
    def rotation_matrix(self, theta) -> np.array:
        return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]])
    

                