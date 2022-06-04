# structures to store TS and NBA

from typing import Dict, Generic, Hashable, List, Set, Tuple, TypeVar, Union


T = TypeVar('T', bound=Hashable)


class StrMap:

    def __init__(self) -> None:
        self.num_str: int = 0
        self.str_to_id: Dict[str, int] = {}
        self.id_to_str: Dict[int, str] = {}

    def add(self, s: str) -> None:
        self.str_to_id[s] = self.num_str
        self.id_to_str[self.num_str] = s
        self.num_str += 1


class TS(Generic[T]):

    def __init__(self) -> None:
        self.num_states: int = 0
        self.action_set = StrMap() # useless
        self.trans: List[Tuple[T, int, T]] = [] # transitions (s, a) -> s'
        self.trans_map: Dict[Tuple[T, int], List[T]] = {} # transisions (s, a) -> all s'
        self.I: List[T] = [] # initial states
        self.AP: Dict[T, Set[int]] = {}  # atomic propositions s_i -> L(s_i)

    def add_action(self, s: str) -> None:
        self.action_set.add(s)

    def add_trans(self, x: T, a: Union[int, str], y: T) -> None:
        if isinstance(a, str):
            a = self.action_set.str_to_id[a]
        self.trans.append((x, a, y))
        if (x, a) in self.trans_map:
            self.trans_map[(x, a)].append(y)
        else:
            self.trans_map[(x, a)] = [y]


class NBA(Generic[T]):

    def __init__(self, Q: List[T], Q0: List[T], F: List[T]) -> None:
        self.Q = Q
        self.Q0 = Q0
        self.F = F
        self.num_states = len(Q)
        self.trans: Dict[Tuple[T, Tuple[int, ...]], List[T]] = {} # transitions (q. a) -> q'
        self.state_map: Dict[T, int] = {}
        for i, q in enumerate(self.Q):
            self.state_map[q] = i
        self.aug_map: Dict[T, int] = None
        self.in_count: Dict[T, int] = {q : 0 for q in self.Q}

    def add_trans(self, q: T, a: Tuple[int, ...], qq: T) -> None:
        aa = list(a)
        aa.sort()
        a = tuple(aa)
        if (q, a) in self.trans:
            self.trans[(q, a)].append(qq)
        else:
            self.trans[(q, a)] = [qq]
        self.in_count[qq] += 1
    
    def get(self, q: T, a: Tuple[int, ...]) -> List[T]:
        return self.trans.get((q, a), [])

    def get_id(self, s: int, q: T) -> int:
        return s * self.num_states + self.state_map[q]

    def simplify(self) -> None:
        # remove states that cannot be reached
        self.Q = [q for q in self.Q if self.in_count[q] > 0]
        self.Q0 = [q0 for q0 in self.Q0 if self.in_count[q0] > 0]
        self.F = [f for f in self.F if self.in_count[f] > 0]
        self.num_states = len(self.Q)
        rm_keys = []
        for (q, a) in self.trans.keys():
            if self.in_count[q] == 0:
                rm_keys.append((q, a))
        for k in rm_keys:
            del self.trans[k]

    def print(self) -> None:
        if self.aug_map is not None:
            print('---- NBA ----')
            print(f'num states = {self.num_states}')
            print(f'initial states: {[(self.aug_map[q], i) for (q, i) in self.Q0]}')
            print(f'final states: {[(self.aug_map[q], i) for (q, i) in self.F]}')
            print('transitions:')
            for ((q, i), a), qq in self.trans.items():
                # print(f'({self.aug_map[q]}, {i}) --- {a} --> {[(self.aug_map[q_[0]], q_[1]) for q_ in qq]}')
                print(f'[{self.state_map[(q, i)]}]({self.aug_map[q]}, {i}) --- {a} --> {[self.state_map[q_] for q_ in qq]}')
            print('---- END ----')


class GNBA(Generic[T]):

    def __init__(self, Q: List[T], Q0: List[T], F: List[List[T]]) -> None:
        self.Q = Q
        self.Q0 = Q0
        self.F = F
        self.num_states = len(Q)
        self.trans: Dict[Tuple[T, Tuple[int, ...]], List[T]] = {} # transitions (q. a) -> q'
        self.state_map: Dict[T, int] = {}
        for i, q in enumerate(self.Q):
            self.state_map[q] = i

    def add_trans(self, q: T, a: Tuple[int, ...], qq: T) -> None:
        aa = list(a)
        aa.sort()
        a = tuple(aa)
        if (q, a) in self.trans:
            self.trans[(q, a)].append(qq)
        else:
            self.trans[(q, a)] = [qq]

    def get(self, q: T, a: Tuple[int, ...]) -> List[T]:
        return self.trans.get((q, a), [])

    def print(self) -> None:
        print('---- GNBA ----')
        print(f'num states = {self.num_states}')
        print(f'initial states: {[self.state_map[q] for q in self.Q0]}')
        print('final state sets:')
        for ql in self.F:
            print([self.state_map[q] for q in ql])
        print('transitions:')
        for (q, a), qq in self.trans.items():
            print(f'{self.state_map[q]} --- {a} --> {[self.state_map[q_] for q_ in qq]}')
        print('---- END ----')
