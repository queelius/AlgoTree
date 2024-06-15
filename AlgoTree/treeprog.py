from typing import Any, Callable, Dict, List, Tuple
import copy
import deque

class Dispatcher:
    def __init__(self):
        self.funcs = {}

    def register(self, name, func, expected_args=None):
        self.funcs[name] = {"func": func, "expected_args": expected_args or []}

    def get(self, name):
        entry = self.funcs.get(name, {"func": lambda *args, **kwargs: None, "expected_args": []})
        return entry["func"], entry["expected_args"]

    def call(self, name, env, *args, **kwargs):
        func, expected_args = self.get(name)
        parsed_args, parsed_kwargs = self.parse_args(expected_args, env, *args, **kwargs)
        return func(*parsed_args, **parsed_kwargs)

    def parse_args(self, expected_args, env, *args, **kwargs):
        parsed_args = []
        parsed_kwargs = {}
        for expected in expected_args:
            if isinstance(expected, tuple):
                key, default = expected
                if key in kwargs:
                    parsed_kwargs[key] = kwargs[key]
                elif key in env.frame:
                    parsed_kwargs[key] = env.get(key)
                else:
                    parsed_kwargs[key] = default
            else:
                parsed_args.append(args[0])
                args = args[1:]
        return parsed_args, parsed_kwargs


class TreeTraversal:
    """
    Tree traversal evaluator with support for payload mapping and flexible traversal actions.
    """

    def __init__(self,
                 program: List[Dict[str, Any]] = None,
                 max_depth: int = float("inf"),
                 max_results: int = float("inf"),
                 max_visited: int = float("inf"),
                 queue: Callable = deque,
                 dispatchers: Dict[str, Dispatcher] = None):

        self.program = program if program is not None else []
        self.max_depth = max_depth
        self.max_results = max_results
        self.max_visited = max_visited
        self.queue = queue()
        self.dispatcher = dispatchers if dispatchers is not None else {
            'pred': Dispatcher(),
            'func': Dispatcher(),
            'selector': Dispatcher(),
            'order': Dispatcher(),
            'follower': Dispatcher(),
            'payload-map': Dispatcher()
        }

    def set_dispatcher(self, type: str, dispatcher: Dispatcher):
        if type not in self.dispatcher:
            raise ValueError(f"Invalid dispatcher type: {type}")
        self.dispatcher[type] = dispatcher

    def register(self, type: str, name: str, func: Callable, expected_args=None):
        if type not in self.dispatcher:
            raise ValueError(f"Invalid dispatcher type: {type}")
        self.dispatcher[type].register(name, func, expected_args)

    def _get_result_name(self, results: Dict, action: Dict[str, Any], prefix: str) -> str:
        result_name = action.get("result-name")
        if result_name:
            return result_name
        return prefix if prefix not in results else f"{prefix}-{hash(str(action)) % 10000}"

    def eval(self, node:
             Any, program: List[Dict[str, Any]] = None,
             env: Environment = None,
             **kwargs) -> Dict[str, List[Tuple[Any, int]]]:
        if program is None:
            program = self.convert_kwargs_to_program(kwargs)
        else:
            program = self.override_program_with_kwargs(program, kwargs)

        env = env or Environment()
        stack = [(node, 0, iter(program), env)]
        results = {}

        while stack:
            node, depth, program_iter, env = stack.popleft()
            if depth > self.max_depth:
                continue

            action = next(program_iter, None)
            while action:
                if 'visit' in action:
                    pred_func_name = action["visit"]
                    result_name = self._get_result_name(results, action, pred_func_name)
                    pred_args = action.get("args", [])
                    pred_kwargs = action.get("kwargs", {})
                    if self.dispatcher['pred-func'](pred_func_name, node, env, *pred_args, **pred_kwargs):
                        if result_name not in results:
                            results[result_name] = []
                        results[result_name].append((node, depth))
                        total_results = sum(len(result) for result in results.values())
                        if total_results >= self.max_results:
                            return results
                elif "payload-map" in action:
                    map_func_name = action["payload-map"]
                    map_args = action.get("args", [])
                    map_kwargs = action.get("kwargs", {})
                    node.payload = self.dispatcher['func'](map_func_name, node, *map_args, **map_kwargs)
                elif "cond" in action:
                    for pred_func_name, sub_program in action["cond"]:
                        if self.dispachter['pred-func'](pred_func_name, 
                            program_iter = iter(sub_program + list(program_iter))
                            break
                elif "dir" in action:
                    dir_name = action["dir"]
                    follow_func, expected_args = self.dispatcher['follower'].get(dir_name)
                    next_nodes = follow_func(node)

                    select_action = action.get("select", "all")
                    sel_func, expected_args = self.dispatcher['selector'].get(select_action)
                    selected = sel_func(next_nodes)

                    order_action = action.get("selected-order", "identity")
                    sel_order_func, expected_args = self.dispatcher['order'].get(order_action)
                    ordered_selected = sel_order_func(selected

                    new_env = env.extend()
                    self.queue.extend((next_node, depth + 1, iter(program), new_env) for next_node in ordered_selected)
                else:
                    raise ValueError(f"Invalid action in program: {action}")
                action = next(program_iter, None)

        return results

    def convert_kwargs_to_program(self, kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        program = []
        for key, value in kwargs.items():
            if isinstance(value, dict):
                program.append(value)
            else:
                program.append({key: value})
        return program

    def override_program_with_kwargs(self, program: List[Dict[str, Any]], kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        new_program = self.convert_kwargs_to_program(kwargs)
        if new_program:
            return new_program
        return program
