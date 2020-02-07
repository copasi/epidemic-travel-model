import numpy as np


class agent():
    def __init__(self, group, condition):
        self.group = group
        self.condition = condition

    def change_condition(self, new_cond):
        self.condition = new_cond

    def change_group(self, new_group):
        self.group = new_group


class group():

    _trans_rate = trans_rate = {'S': ('E', 0.2),
                                'E': ('I', 0.1),
                                'I': ('R', 0.1)}

    def __init__(self, name, population, ratio):
        self.name = name
        self.population = population
        self.S = int(self.population * ratio['S'])
        self.E = int(self.population * ratio['E'])
        self.I_ = int(self.population * ratio['I'])
        self.R = self.population - self.S - self.E - self.I_
        self.agent = []
        for i in range(self.S):
            self.agent.append(agent(self.name, 'S'))
        for i in range(self.E):
            self.agent.append(agent(self.name, 'E'))
        for i in range(self.I_):
            self.agent.append(agent(self.name, 'I'))
        for i in range(self.R):
            self.agent.append(agent(self.name, 'R'))

    def update_cond(self):
        p_S_E = self._trans_rate['S'][1] * self.I_ / self.population
        # print(p_S_E)
        p_E_I = self._trans_rate['E'][1]
        p_I_R = self._trans_rate['I'][1]
        for agent in self.agent:
            if agent.condition == 'S':
                if np.random.random() < p_S_E:
                    agent.change_condition('E')
                    self.E += 1
                    self.S -= 1
            elif agent.condition == 'E':
                if np.random.random() < p_E_I:
                    agent.change_condition('I')
                    self.I_ += 1
                    self.E -= 1
            elif agent.condition == 'I':
                if np.random.random() < p_I_R:
                    agent.change_condition('R')
                    self.R += 1
                    self.I_ -= 1

    def pop(self):
        # print(len(self.agent), self.population)
        agent = self.agent.pop(np.random.randint(self.population))
        self.population -= 1
        if agent.condition == 'S':
            self.S -= 1
        elif agent.condition == 'E':
            self.E -= 1
        elif agent.condition == 'I':
            self.I_ -= 1
        if agent.condition == 'R':
            self.R -= 1
        return agent

    def push(self, agent):
        self.population += 1
        agent.group = self.name
        self.agent.append(agent)
        if agent.condition == 'S':
            self.S += 1
        elif agent.condition == 'E':
            self.E += 1
        elif agent.condition == 'I':
            self.I_ += 1
        if agent.condition == 'R':
            self.R += 1


def migrate(groups):
    migration_rate = 0.05

    np.random.shuffle(groups)
    for i in range(N):
        migrate_count = int(groups[i].population * migration_rate / (N - 1))
        for j in range(N):
            if j == i:
                continue
            for k in range(migrate_count):
                groups[j].push(groups[i].pop())


def update(groups):
    S, E, I_, R = 0, 0, 0, 0
    for i in range(N):
        groups[i].update_cond()
        S += groups[i].S
        E += groups[i].E
        I_ += groups[i].I_
        R += groups[i].R
    return (S, E, I_, R)


if __name__ == '__main__':
    N = 5
    population = 10000
    init_ratio = 0.1
    steps = 1000

    groups = []
    for i in range(N):
        if not i:
            ratio = {'S': 1. - init_ratio, 'E': 0., 'I': init_ratio, 'R': 0.}
        else:
            ratio = {'S': 1., 'E': 0., 'I': 0., 'R': 0.}
        groups.append(group(i, population, ratio))

    for i in range(steps):
        print(i, update(groups))
        migrate(groups)

