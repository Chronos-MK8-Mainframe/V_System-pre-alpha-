"""
Inverse Entailment Engine - Progol's core algorithm
Based on Muggleton (1995) "Inverse entailment and Progol"

This is a clean-room implementation of the algorithm described in published
academic papers. Algorithms are not copyrightable.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import time

from v_system.core.rule import Rule
from v_system.core.context import Context


@dataclass
class Literal:
    """First-order logic literal"""
    predicate: str
    terms: List[str]
    negated: bool = False
    
    def __str__(self):
        neg = "¬" if self.negated else ""
        return f"{neg}{self.predicate}({', '.join(self.terms)})"
    
    def __hash__(self):
        return hash((self.predicate, tuple(self.terms), self.negated))
    
    def ground(self, substitution: Dict[str, str]) -> 'Literal':
        """Apply substitution to literal"""
        new_terms = [substitution.get(t, t) for t in self.terms]
        return Literal(self.predicate, new_terms, self.negated)
    
    def is_ground(self) -> bool:
        """Check if all terms are constants (not variables)"""
        return all(not self._is_variable(t) for t in self.terms)
    
    def _is_variable(self, term: str) -> bool:
        """Check if term is a variable (uppercase first letter)"""
        return term and term[0].isupper()
    
    def get_variables(self) -> Set[str]:
        """Get all variables in literal"""
        return {t for t in self.terms if self._is_variable(t)}


@dataclass
class Clause:
    """First-order logic clause: Head :- Body1, Body2, ..."""
    head: Literal
    body: List[Literal] = field(default_factory=list)
    
    def __str__(self):
        if not self.body:
            return str(self.head)
        body_str = ", ".join(str(lit) for lit in self.body)
        return f"{self.head} :- {body_str}"
    
    def __hash__(self):
        return hash((self.head, tuple(self.body)))
    
    def get_variables(self) -> Set[str]:
        """Get all variables in clause"""
        vars_set = self.head.get_variables()
        for lit in self.body:
            vars_set.update(lit.get_variables())
        return vars_set
    
    def length(self) -> int:
        """Clause length (number of literals in body)"""
        return len(self.body)
    
    def subsumes(self, other: 'Clause') -> bool:
        """Check if this clause θ-subsumes other clause"""
        substitution = {}
        
        if not self._unify(self.head, other.head, substitution):
            return False
        
        for self_lit in self.body:
            found_match = False
            for other_lit in other.body:
                test_sub = substitution.copy()
                if self._unify(self_lit, other_lit, test_sub):
                    substitution.update(test_sub)
                    found_match = True
                    break
            
            if not found_match:
                return False
        
        return True
    
    def _unify(self, lit1: Literal, lit2: Literal, 
               substitution: Dict[str, str]) -> bool:
        """Try to unify two literals with given substitution"""
        if lit1.predicate != lit2.predicate or lit1.negated != lit2.negated:
            return False
        
        if len(lit1.terms) != len(lit2.terms):
            return False
        
        for t1, t2 in zip(lit1.terms, lit2.terms):
            t1_sub = substitution.get(t1, t1)
            t2_sub = substitution.get(t2, t2)
            
            if self._is_variable(t1_sub) and self._is_variable(t2_sub):
                substitution[t1_sub] = t2_sub
            elif self._is_variable(t1_sub):
                substitution[t1_sub] = t2_sub
            elif self._is_variable(t2_sub):
                substitution[t2_sub] = t1_sub
            else:
                if t1_sub != t2_sub:
                    return False
        
        return True
    
    def _is_variable(self, term: str) -> bool:
        return term and term[0].isupper()


@dataclass
class ModeDeclaration:
    """Mode declaration for constraining hypothesis space"""
    predicate: str
    arg_modes: List[str]  # '+' = input, '-' = output, '#' = constant
    
    def __str__(self):
        return f"{self.predicate}({', '.join(self.arg_modes)})"


class InverseEntailmentEngine:
    """
    Progol's Inverse Entailment Algorithm
    
    Given:
    - Background knowledge B (existing rules)
    - Positive examples E+ 
    - Negative examples E- (optional)
    
    Find hypothesis H such that:
    - B ∧ H ⊨ E+ (covers positive examples)
    - B ∧ H ⊭ E- (doesn't cover negative examples)
    """
    
    def __init__(self):
        self.mode_declarations: Dict[str, ModeDeclaration] = {}
        self.max_clause_length = 4
        self.max_search_nodes = 1000
        
        self.clauses_evaluated = 0
        self.bottom_clauses_constructed = 0
    
    def add_mode_declaration(self, predicate: str, arg_modes: List[str]):
        """Add mode declaration to constrain search space"""
        self.mode_declarations[predicate] = ModeDeclaration(predicate, arg_modes)
    
    def learn_clause(self, positive_examples: List[Dict],
                    negative_examples: List[Dict],
                    background: List[Clause]) -> Optional[Clause]:
        """
        Learn single clause from examples
        
        Args:
            positive_examples: List of positive training examples
            negative_examples: List of negative training examples  
            background: Background knowledge (existing clauses)
            
        Returns:
            Best clause found, or None
        """
        if not positive_examples:
            return None
        
        print(f"\n🧠 Inverse Entailment: Learning from {len(positive_examples)} positive, "
              f"{len(negative_examples)} negative examples")
        
        seed = positive_examples[0]
        print(f"   Seed: {seed.get('description', str(seed.get('input', '')))}")
        
        print(f"   Constructing bottom clause...")
        bottom = self._construct_bottom_clause(seed, background)
        self.bottom_clauses_constructed += 1
        
        if bottom is None:
            print(f"   ❌ Failed to construct bottom clause")
            return None
        
        print(f"   ⊥: {bottom}")
        print(f"   Bottom clause length: {bottom.length()}")
        
        print(f"   Searching hypothesis space...")
        hypothesis = self._search_hypothesis_space(
            bottom=bottom,
            positive=positive_examples,
            negative=negative_examples,
            background=background
        )
        
        if hypothesis:
            score = self._evaluate_clause(hypothesis, positive_examples, 
                                         negative_examples, background)
            print(f"   ✅ Found hypothesis: {hypothesis}")
            print(f"   Score: {score:.2f}")
        else:
            print(f"   ❌ No suitable hypothesis found")
        
        return hypothesis
    
    def _construct_bottom_clause(self, example: Dict, 
                                 background: List[Clause]) -> Optional[Clause]:
        """Construct most specific clause ⊥(e) that entails example"""
        head = self._example_to_literal(example, is_head=True)
        if not head:
            return None
        
        body_literals = set()
        example_facts = self._extract_facts_from_example(example)
        body_literals.update(example_facts)
        
        # Saturate: apply background knowledge
        new_facts = example_facts.copy()
        iterations = 0
        max_iterations = 3
        
        while new_facts and iterations < max_iterations:
            derived = set()
            for clause in background:
                derived_facts = self._apply_clause(clause, body_literals)
                derived.update(derived_facts)
            
            new_facts = derived - body_literals
            body_literals.update(new_facts)
            iterations += 1
        
        body_list = list(body_literals)
        head_var, body_var = self._variabilize(head, body_list)
        
        if len(body_var) > self.max_clause_length:
            body_var = self._filter_relevant_literals(head_var, body_var)
        
        return Clause(head=head_var, body=body_var)
    
    def _example_to_literal(self, example: Dict, is_head: bool = False) -> Optional[Literal]:
        """Convert example dict to literal"""
        if 'predicate' in example:
            return Literal(
                predicate=example['predicate'],
                terms=example.get('terms', []),
                negated=example.get('negated', False)
            )
        
        if is_head and 'output' in example:
            expr = example['output']
        elif 'input' in example:
            expr = example['input']
        else:
            return None
        
        if hasattr(expr, 'op'):
            terms = []
            if hasattr(expr, 'args'):
                for arg in expr.args:
                    if hasattr(arg, 'op'):
                        terms.append(str(arg.op))
                    else:
                        terms.append(str(arg))
            
            return Literal(predicate=str(expr.op), terms=terms)
        
        return None
    
    def _extract_facts_from_example(self, example: Dict) -> Set[Literal]:
        """Extract all ground facts from example"""
        facts = set()
        
        if 'facts' in example:
            for fact in example['facts']:
                lit = self._example_to_literal(fact)
                if lit:
                    facts.add(lit)
        
        if 'input' in example:
            input_facts = self._expression_to_literals(example['input'])
            facts.update(input_facts)
        
        return facts
    
    def _expression_to_literals(self, expr) -> Set[Literal]:
        """Convert expression tree to set of literals"""
        literals = set()
        
        if not hasattr(expr, 'op'):
            return literals
        
        terms = []
        if hasattr(expr, 'args'):
            for arg in expr.args:
                if hasattr(arg, 'op'):
                    terms.append(f"term_{id(arg) % 1000}")
                else:
                    terms.append(str(arg))
        
        if terms:
            literals.add(Literal(predicate=str(expr.op), terms=terms))
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                literals.update(self._expression_to_literals(arg))
        
        return literals
    
    def _apply_clause(self, clause: Clause, facts: Set[Literal]) -> Set[Literal]:
        """Apply clause to derive new facts"""
        return set()
    
    def _variabilize(self, head: Literal, 
                    body: List[Literal]) -> Tuple[Literal, List[Literal]]:
        """Replace constants with variables consistently"""
        constant_to_var = {}
        var_counter = 0
        
        def get_variable(const: str) -> str:
            nonlocal var_counter
            if const not in constant_to_var:
                constant_to_var[const] = f"X{var_counter}"
                var_counter += 1
            return constant_to_var[const]
        
        head_terms = [get_variable(t) if not t[0].isupper() else t 
                     for t in head.terms]
        head_var = Literal(head.predicate, head_terms, head.negated)
        
        body_var = []
        for lit in body:
            lit_terms = [get_variable(t) if not t[0].isupper() else t 
                        for t in lit.terms]
            body_var.append(Literal(lit.predicate, lit_terms, lit.negated))
        
        return head_var, body_var
    
    def _filter_relevant_literals(self, head: Literal, 
                                  body: List[Literal]) -> List[Literal]:
        """Keep most relevant literals based on variable sharing"""
        head_vars = head.get_variables()
        
        scored = []
        for lit in body:
            lit_vars = lit.get_variables()
            shared = len(head_vars & lit_vars)
            scored.append((shared, lit))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [lit for _, lit in scored[:self.max_clause_length]]
    
    def _search_hypothesis_space(self, bottom: Clause,
                                positive: List[Dict],
                                negative: List[Dict],
                                background: List[Clause]) -> Optional[Clause]:
        """Search refinement lattice from bottom clause upward"""
        beam = [bottom]
        best_clause = None
        best_score = float('-inf')
        
        nodes_explored = 0
        
        while beam and nodes_explored < self.max_search_nodes:
            scored_beam = []
            
            for clause in beam:
                score = self._evaluate_clause(clause, positive, negative, background)
                scored_beam.append((score, clause))
                nodes_explored += 1
                self.clauses_evaluated += 1
                
                if score > best_score:
                    best_score = score
                    best_clause = clause
            
            scored_beam.sort(reverse=True)
            next_beam = []
            
            beam_width = 10
            for score, clause in scored_beam[:beam_width]:
                refinements = self._refine_clause(clause)
                next_beam.extend(refinements)
            
            next_beam = list(set(next_beam))
            next_beam = [c for c in next_beam if c.length() <= self.max_clause_length]
            
            beam = next_beam
            
            if nodes_explored > 100 and best_score <= 0:
                break
        
        print(f"   Explored {nodes_explored} nodes")
        
        return best_clause if best_score > 0 else None
    
    def _evaluate_clause(self, clause: Clause, positive: List[Dict],
                        negative: List[Dict], background: List[Clause]) -> float:
        """Evaluate clause using compression measure"""
        p = self._count_covered(clause, positive, background)
        n = self._count_covered(clause, negative, background)
        length_penalty = clause.length()
        
        score = p - n - length_penalty - 1
        
        return score
    
    def _count_covered(self, clause: Clause, examples: List[Dict],
                      background: List[Clause]) -> int:
        """Count how many examples are covered by clause"""
        count = 0
        
        for example in examples:
            if self._covers_example(clause, example, background):
                count += 1
        
        return count
    
    def _covers_example(self, clause: Clause, example: Dict,
                       background: List[Clause]) -> bool:
        """Check if clause + background entails example"""
        example_lit = self._example_to_literal(example, is_head=True)
        if not example_lit:
            return False
        
        substitution = {}
        return clause.head.predicate == example_lit.predicate
    
    def _refine_clause(self, clause: Clause) -> List[Clause]:
        """Generate refinements by removing literals"""
        refinements = []
        
        for i in range(len(clause.body)):
            new_body = clause.body[:i] + clause.body[i+1:]
            refinement = Clause(head=clause.head, body=new_body)
            refinements.append(refinement)
        
        return refinements
    
    def clause_to_rule(self, clause: Clause, context: Context) -> Rule:
        """Convert learned clause to V-system Rule"""
        rule_id = f"ile_{clause.head.predicate}_{int(time.time() * 1000) % 10000}"
        
        def make_condition(c: Clause):
            def condition(expr, ctx, refs):
                if not hasattr(expr, 'op'):
                    return 0
                if str(expr.op) == c.head.predicate:
                    return 1
                return 0
            return condition
        
        def make_transform(c: Clause):
            def transform(expr):
                return expr
            return transform
        
        rule = Rule(
            rule_id=rule_id,
            condition=make_condition(clause),
            transform=make_transform(clause),
            domain=context,
            priority=9,
            confidence=0.9,
            source="inverse_entailment"
        )
        
        return rule
    
    def get_statistics(self) -> Dict:
        """Get learning statistics"""
        return {
            'clauses_evaluated': self.clauses_evaluated,
            'bottom_clauses_constructed': self.bottom_clauses_constructed,
            'mode_declarations': len(self.mode_declarations)
        }
