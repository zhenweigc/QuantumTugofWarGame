from typing import List, Optional
import numpy as np
import random
from GamePlayer import *

'''
Insert high-level explanation of your strategy here. Why did you design this strategy?
When should it work well, and when should it have trouble?

1) Why did you design this strategy?

We first noticed that we need to record the current states of the qubit. After analyzing
the game play file, we realized that the state update should be different for team 0 and team 1.
For team 0, the previous actions include team 0's action in the previous round and team 1's action
in the previous round. The current state should be updated by these two operations followed by a rotation.
For team 1, the previous actions include team 1's action in the previous round and team 0's action in the
current round. Therefore, the current state shoud be updated by actions in the order of team 1'action,
a rotation, and team 0's action.

By analyzing the game rules, we figured out different functionality of different cards,
and can make different effects on different playing stage.
For example, the REVERSE card can reverse the $\theta$ rotation direction of qubit,
and PAULIZ card can also make similar effect by phasefliping the qubit.
But the effect of these REVERSE and PAULIZ cards are kind of non-immediate,
as it takes turns to accumulate the effect of rotations.
So, these REVERSE and PAULIZ cards are more suitable to play on the earlier stage (< 99 rounds).
On the other hand, the HADAMARD and PAULIX cards can change the qubit state dramatically,
so as to make a reversal to the situation that is going to lose.
So the HADAMARD and PAULIX cards should be stored in hand and play in the final stage
(>= 99 rounds). We also follow the logic that PAULIX is more helpful than HADAMARD,
so we will try to gather as many as PAULIX in hand for the final stage.
The MEASURE card we found it is not that useful in our strategy, so we will play it
out once we get a MEASURE card.

To play the cards properly, we have some conditional checking function for each kind
of cards. For example, for REVERSE, we will check if the REVERSE card can make the
rotation of qubit good for us. Moreover, we also have PAULIZ and HADAMARD conditation
checking functions. Z_Good() and H_good() function will compute the aftermath of
applying such gates, and compare the result with not applying these gates. If chance
of winning increments, then we will use the corresponding card here.

These strategy makes us almost always in a more preferable state for early stages (< 99 rounds),
and this can save us a PAULIX card in the final stage, which enlarges the winning
percentage of our team.

For the final stage, we want to play the strongest card because we do not know how many rounds there
will be after the current round. we also check conditions before play any cards. We only
play PAULIX card if we are going to lose the game. This makes our storing PAULIX cards strategy
more powerful, because we can take advantage of these PAULIX cards to win the game.
We have the assumption that the other teams will also play PAULIX cards in the final
stage if it seems the situation is not good for them. So if we have more PAULIX
cards in hand than the opponents, then we will have more possibilities to win.

2) When should it work well?

Because we are using REVERSE and PAULIZ cards properly in the earlier stage, so
when we accepts some REVERSE or PAULIZ cards and can use them when needed, then
before round 99, we will have a much more larger winning percentage then the opponents.
Since the REVERSE and PAULIZ takes relatively high possibilities,
Z (27%) and R (21%). So this situation almost always happen.

For the final stage, when we stores a sufficient amount of PAULIX cards, then we will
win the game in high possibility.

3) When should it have trouble?

There is a unfavorable situation for our earlier stage playing strategy. If we
turn the rotation direction in a favorable direction to us too early, and we
have already get 5 PAULIX cards, which means we will not again adjust our cards,
then after the coefficient of our team reaches 1.00, it will begin to decrease.
Then properly in the final stage, the situation is not good for us.
To prevent this happen, we design a step accounter, and play REVERSE and
PAULIZ cards intermittently. But this is not always work because the cards
deliver is randomly.

For the final stage, if we just can not receive PAULIX cards because the randomly
deliver cards, then we probably will lose the game. But that's just out of luck
and there is not much we can do.

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
                if GameAction.PAULIX in hand and self.X_good(team, 0) and GameAction.HADAMARD in hand and self.H_good(team):
                    self.num_cards -= 1
                    if self.X_better_than_H(team, 0):
                        return GameAction.PAULIX
                    else:
                        return GameAction.HADAMARD

                if GameAction.PAULIX in hand and self.X_good(team, 0):
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

    '''
    Rotate() function return a boolean.
    It indicates if rotating at this moment is actually useful or not.
    '''
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

    '''
    Check if using a Z-gate is useful by comparing the result before and after
    applying such gate. If our team has a better chance of winning, then it is
    good.
    '''
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

    '''
    Check if using a H-gate is useful by the same way as what we did in Z_Good()
    '''
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

    '''
    Return if using a X gate here is worth it
    diff is a threshold.
    '''
    def X_good(self, team, diff) -> bool:
        temp_state = self.cur_state;
        temp_rt = rotation_matrix(self.cur_direction * self.theta);
        #If not applying X gate here.
        temp_me = np.absolute(np.dot(temp_rt, temp_state)[team]);
        #if (temp_me >= 1 - np.absolute(diff)):
        #    return False;

        X = np.array([[0, 1], [1, 0]]);
        temp_state = np.dot(temp_rt, np.dot(X, temp_state));
        temp_after = np.absolute(temp_state[team]);
        if (temp_me**2 + np.absolute(diff) < temp_after**2):
            return True;
        else:
            return False;

    '''
    Check if using X gate is better than using H gate

    Caution: This function does not check if using X/H is a good idea comparing
    to not using any of them.
    '''
    def X_better_than_H(self, team, diff) -> bool:
         temp_state = self.cur_state;
         temp_rt = rotation_matrix(self.cur_direction * self.theta);
         #temp_me = np.absolute(np.dot(temp_rt, temp_state)[team]);

         X = np.array([[0, 1], [1, 0]]);
         H = np.array([[np.sqrt(1/2), np.sqrt(1/2)], [np.sqrt(1/2), -np.sqrt(1/2)]]);

         temp_state_X = np.dot(temp_rt, np.dot(X, temp_state));
         temp_state_H = np.dot(temp_rt, np.dot(H, temp_state));

         temp_after_X = np.absolute(temp_state_X[team]);
         temp_after_H = np.absolute(temp_state_H[team]);

         if temp_after_H**2 + np.absolute(diff) < temp_after_X**2:
             return True;
         else:
             return False;

    def rotation_matrix(self, theta) -> np.array:
        return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]])
