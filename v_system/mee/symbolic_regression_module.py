"""Symbolic regression for rule synthesis"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import random
import math

from v_system.core.rule import Rule
from v_system.core.context import Context


@dataclass
class Expression:
    """Symbolic expression tree"""
    op: str
    args: List['Expression']
    value: Optional[float] = None
    
    def evaluate(self, variables: Dict[str, float]) -> float:
        """Evaluate expression with given variable values"""
        if self.value is not None:
            return self.value
        
        if self.op in variables:
            return variables[self.op]
        
        if not self.args:
            return 0.0
        
        arg_values = [arg.evaluate(variables) for arg in self.args]
        return self._apply_operation(self.op, arg_values)
    
    def _apply_operation(self, op: str, args: List[float]) -> float:
        """Apply operation to arguments"""
        try:
            if op == '+':
                return sum(args)
            elif op == '-':
                return args[0] - sum(args[1:]) if len(args) > 1 else -args[0]
            elif op == '*':
                result = 1.0
                for arg in args:
                    result *= arg
                return result
            elif op == '/':
                if len(args) == 2 and args[1] != 0:
                    return args[0] / args[1]
                return 0.0
            elif op == '^':
                if len(args) == 2:
                    return args[0] ** args[1]
                return 0.0
            elif op == 'sin':
                return math.sin(args[0]) if args else 0.0
            elif op == 'cos':
                return math.cos(args[0]) if args else 0.0
            elif op == 'exp':
                return math.exp(min(args[0], 100)) if args else 0.0
            elif op == 'log':
                return math.log(args[0]) if args and args[0] > 0 else 0.0
            else:
                return args[0] if args else 0.0
        except:
            return 0.0
    
    def copy(self):
        """Create deep copy of expression"""
        return Expression(
            op=self.op,
            args=[arg.copy() for arg in self.args],
            value=self.value
        )
    
    def size(self) -> int:
        """Get size (number of nodes) in expression tree"""
        return 1 + sum(arg.size() for arg in self.args)
    
    def depth(self) -> int:
        """Get depth of expression tree"""
        if not self.args:
            return 1
        return 1 + max(arg.depth() for arg in self.args)
    
    def __str__(self) -> str:
        if self.value is not None:
            return str(self.value)
        if not self.args:
            return self.op
        if len(self.args) == 1:
            return f"{self.op}({self.args[0]})"
        if len(self.args) == 2 and self.op in ['+', '-', '*', '/', '^']:
            return f"({self.args[0]} {self.op} {self.args[1]})"
        return f"{self.op}({', '.join(str(arg) for arg in self.args)})"


class SymbolicRegressor:
    """Symbolic regression engine for discovering transformation rules"""
    
    def __init__(self):
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.tournament_size = 3
        self.max_depth = 5
        
        self.operations = ['+', '-', '*', '/']
        self.functions = ['sin', 'cos']
        
    def synthesize_rule(self, examples: List[Dict], 
                       context: Context) -> Optional[Tuple[Expression, float]]:
        """Synthesize transformation rule from examples using genetic programming"""
        if len(examples) < 2:
            return None
        
        variables = self._extract_variables(examples)
        
        if not variables:
            return None
        
        population = [self._generate_random_expression(variables) 
                     for _ in range(self.population_size)]
        
        best_expr = None
        best_fitness = float('inf')
        
        for generation in range(self.generations):
            fitness_scores = [self._evaluate_fitness(expr, examples, variables) 
                            for expr in population]
            
            min_fitness_idx = fitness_scores.index(min(fitness_scores))
            if fitness_scores[min_fitness_idx] < best_fitness:
                best_fitness = fitness_scores[min_fitness_idx]
                best_expr = population[min_fitness_idx].copy()
            
            if best_fitness < 0.001:
                break
            
            new_population = []
            
            elite_count = self.population_size // 10
            elite_indices = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i])[:elite_count]
            new_population.extend([population[i].copy() for i in elite_indices])
            
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1 = self._tournament_select(population, fitness_scores)
                    parent2 = self._tournament_select(population, fitness_scores)
                    child = self._crossover(parent1, parent2)
                else:
                    child = self._tournament_select(population, fitness_scores).copy()
                
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, variables)
                
                new_population.append(child)
            
            population = new_population
        
        if best_expr and best_fitness < 1.0:
            return (best_expr, best_fitness)
        
        return None
    
    def _extract_variables(self, examples: List[Dict]) -> List[str]:
        """Extract variable names from examples"""
        variables = set()
        
        for example in examples:
            input_vars = self._get_expression_variables(example['input'])
            variables.update(input_vars)
        
        return list(variables)
    
    def _get_expression_variables(self, expr) -> List[str]:
        """Get variables from expression"""
        variables = []
        
        if not hasattr(expr, 'op'):
            if hasattr(expr, 'value') and isinstance(expr.value, str):
                variables.append(expr.value)
            return variables
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                variables.extend(self._get_expression_variables(arg))
        
        return list(set(variables))
    
    def _generate_random_expression(self, variables: List[str], 
                                   depth: int = 0) -> Expression:
        """Generate random expression tree"""
        if depth >= self.max_depth or (depth > 0 and random.random() < 0.3):
            if random.random() < 0.5 and variables:
                return Expression(op=random.choice(variables), args=[], value=None)
            else:
                return Expression(op='const', args=[], 
                                value=random.uniform(-5, 5))
        
        if random.random() < 0.7:
            op = random.choice(self.operations)
            left = self._generate_random_expression(variables, depth + 1)
            right = self._generate_random_expression(variables, depth + 1)
            return Expression(op=op, args=[left, right])
        else:
            func = random.choice(self.functions)
            arg = self._generate_random_expression(variables, depth + 1)
            return Expression(op=func, args=[arg])
    
    def _evaluate_fitness(self, expr: Expression, examples: List[Dict],
                         variables: List[str]) -> float:
        """Evaluate fitness of expression (lower is better)"""
        total_error = 0.0
        
        for example in examples:
            try:
                var_values = self._extract_variable_values(example['input'], variables)
                predicted = expr.evaluate(var_values)
                expected = self._get_output_value(example['output'])
                error = abs(predicted - expected)
                total_error += error
            except Exception:
                total_error += 1000.0
        
        complexity_penalty = expr.size() * 0.01 + expr.depth() * 0.05
        
        return total_error / len(examples) + complexity_penalty
    
    def _extract_variable_values(self, expr, variables: List[str]) -> Dict[str, float]:
        """Extract variable values from expression"""
        values = {}
        
        for var in variables:
            value = self._find_variable_value(expr, var)
            if value is not None:
                values[var] = value
            else:
                values[var] = 0.0
        
        return values
    
    def _find_variable_value(self, expr, var_name: str) -> Optional[float]:
        """Find value of variable in expression"""
        if not hasattr(expr, 'op'):
            return None
        
        if str(expr.op) == var_name and hasattr(expr, 'value'):
            try:
                return float(expr.value)
            except (ValueError, TypeError):
                return None
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                result = self._find_variable_value(arg, var_name)
                if result is not None:
                    return result
        
        return None
    
    def _get_output_value(self, output_expr) -> float:
        """Get numeric value from output expression"""
        if hasattr(output_expr, 'value'):
            try:
                return float(output_expr.value)
            except (ValueError, TypeError):
                return 0.0
        return 0.0
    
    def _tournament_select(self, population: List[Expression],
                          fitness_scores: List[float]) -> Expression:
        """Select individual using tournament selection"""
        tournament_indices = random.sample(range(len(population)), 
                                         self.tournament_size)
        best_idx = min(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]
    
    def _crossover(self, parent1: Expression, parent2: Expression) -> Expression:
        """Perform crossover between two expressions"""
        child = parent1.copy()
        subtree_path = self._random_subtree_path(child)
        subtree = self._get_random_subtree(parent2)
        self._replace_subtree(child, subtree_path, subtree)
        return child
    
    def _mutate(self, expr: Expression, variables: List[str]) -> Expression:
        """Mutate expression"""
        mutation_type = random.choice(['replace', 'modify'])
        
        if mutation_type == 'replace':
            subtree_path = self._random_subtree_path(expr)
            new_subtree = self._generate_random_expression(variables, 
                                                          depth=random.randint(0, 2))
            self._replace_subtree(expr, subtree_path, new_subtree)
        elif mutation_type == 'modify':
            node = self._get_random_node(expr)
            if node.value is not None:
                node.value += random.gauss(0, 1)
            elif node.op in self.operations:
                node.op = random.choice(self.operations)
        
        return expr
    
    def _random_subtree_path(self, expr: Expression) -> List[int]:
        """Get path to random subtree"""
        if not expr.args or random.random() < 0.2:
            return []
        
        child_idx = random.randint(0, len(expr.args) - 1)
        return [child_idx] + self._random_subtree_path(expr.args[child_idx])
    
    def _get_random_subtree(self, expr: Expression) -> Expression:
        """Get random subtree from expression"""
        if not expr.args or random.random() < 0.3:
            return expr.copy()
        
        child = random.choice(expr.args)
        return self._get_random_subtree(child)
    
    def _replace_subtree(self, expr: Expression, path: List[int], 
                        new_subtree: Expression):
        """Replace subtree at path with new subtree"""
        if not path:
            expr.op = new_subtree.op
            expr.args = new_subtree.args
            expr.value = new_subtree.value
            return
        
        current = expr
        for idx in path[:-1]:
            if idx < len(current.args):
                current = current.args[idx]
        
        if path[-1] < len(current.args):
            current.args[path[-1]] = new_subtree
    
    def _get_random_node(self, expr: Expression) -> Expression:
        """Get random node from expression"""
        if not expr.args or random.random() < 0.3:
            return expr
        
        child = random.choice(expr.args)
        return self._get_random_node(child)
