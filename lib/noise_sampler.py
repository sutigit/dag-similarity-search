# sampler.py
import re, json, random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from classes.event_graph import EventGraph
from classes.event_node import EventNode
from data.event_types import event_types  # {int: 'name'}
from pathlib import Path

# small vocabularies for attribute sampling
_EDU_LEVELS = ["primary", "highschool", "bachelor", "master", "phd"]
_INDUSTRIES = ["tech", "finance", "healthcare", "education", "manufacturing", "retail"]
_POSITIONS = ["intern", "junior", "senior", "manager", "director", "executive"]
_CITIES = ["Bangkok", "New York", "London", "Paris", "Tokyo", "Berlin"]
_COUNTRIES = ["Thailand", "USA", "UK", "France", "Japan", "Germany"]
_UNIS = ["Chulalongkorn", "Mahidol", "Harvard", "Oxford", "Tokyo Univ."]
_HOBBIES = ["reading", "sports", "music", "painting", "photography", "gardening"]

def _get_event_spec_by_name(name: str) -> Optional[Dict]:
    for v in event_types.values():
        if v.get("event_type") == name:
            return v
    return None

def generate_event_attributes(name: str, age: Optional[int], rng: random.Random) -> Dict[str, object]:
    """Create plausible random attribute values for the given event `name`.

    - `age` is used when available for the `age` attribute.
    - `time` is a sampled year between 1950 and 2024.
    - categorical attributes are sampled from small vocabularies above.
    """
    spec = _get_event_spec_by_name(name)
    out: Dict[str, object] = {}
    if not spec:
        return out

    attrs = spec.get("attributes", {})
    for k in attrs.keys():
        if k == "age":
            out["age"] = int(age) if age is not None else rng.randint(0, 90)
        elif k == "time":
            # produce a simple year integer; other modules may prefer strings
            out["time"] = rng.randint(1950, 2024)
        elif k == "education_level":
            out["education_level"] = rng.choice(_EDU_LEVELS)
        elif k == "industry":
            out["industry"] = rng.choice(_INDUSTRIES)
        elif k == "position":
            out["position"] = rng.choice(_POSITIONS)
        elif k == "company":
            out["company"] = f"Company_{rng.randint(1,200)}"
        elif k == "city":
            out["city"] = rng.choice(_CITIES)
        elif k == "country":
            out["country"] = rng.choice(_COUNTRIES)
        elif k == "university":
            out["university"] = rng.choice(_UNIS)
        elif k == "hobby":
            out["hobby"] = rng.choice(_HOBBIES)
        else:
            out[k] = rng.choice([None, rng.randint(0, 100), f"val_{rng.randint(0,999)}"])
    return out

# ---------- Rule engine (regex-based, name-agnostic) ----------
@dataclass
class Rule:
    pattern: re.Pattern
    prereqs: List[str] = field(default_factory=list)          # exact event names (or later map via regex too)
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    max_count: Optional[int] = None
    base_rates: List[Tuple[Tuple[int,int], float]] = field(default_factory=list)  # [((a,b), p), ...]

def compile_rules(raw: Dict) -> List[Rule]:
    rules: List[Rule] = []
    def as_rates(d):
        out=[]
        for k,v in d.items():
            a,b = map(int, k.split("-"))
            out.append(((a,b), float(v)))
        return out

    for r in raw.get("rules", []):
        rules.append(Rule(
            pattern=re.compile(r["pattern"]),
            prereqs=r.get("prereqs", []),
            age_min=r.get("age_min"),
            age_max=r.get("age_max"),
            max_count=r.get("max_count"),
            base_rates=as_rates(r.get("base_rates", {}))
        ))
    return rules

def match_rules(rules: List[Rule], name: str) -> List[Rule]:
    return [r for r in rules if r.pattern.search(name)]

def base_rate_for_age(rules_for_e: List[Rule], age: int, default: float) -> float:
    p = None
    for r in rules_for_e:
        for (a,b), prob in r.base_rates:
            if a <= age <= b:
                p = prob if p is None else max(p, prob)  # take max across matches
    return p if p is not None else default

def allowed_by_age(rules_for_e: List[Rule], age: int) -> bool:
    ok = True
    for r in rules_for_e:
        if r.age_min is not None and age < r.age_min: ok = False
        if r.age_max is not None and age > r.age_max: ok = False
    return ok

def prereqs_for(rules_for_e: List[Rule]) -> List[str]:
    out=[]
    for r in rules_for_e:
        out.extend(r.prereqs)
    return list(set(out))

def max_count_for(rules_for_e: List[Rule]) -> Optional[int]:
    caps=[r.max_count for r in rules_for_e if r.max_count is not None]
    return min(caps) if caps else None

# ---------- Sampler (name-agnostic) ----------
def add_event(graph, name, last, *, age: Optional[int] = None, rng: Optional[random.Random] = None):
    """Add an EventNode to `graph`. If `rng` is provided, synthesize attributes using `generate_event_attributes`.

    `age` is used to populate the event's age attribute when applicable.
    """
    attrs = {}
    if rng is not None:
        attrs = generate_event_attributes(name, age, rng)
    node = EventNode(name, event_attributes=attrs)
    graph.add_node(node)
    if last is not None:
        graph.add_edge(last, node)
    return node

def sample_graph(rng: random.Random, max_events: int, rules: List[Rule],
                 age_max_dist=(70,75,80,85,90), age_max_w=(0.1,0.2,0.35,0.25,0.1),
                 default_rate=0.01) -> EventGraph:
    g = EventGraph()
    last = None
    names = [v["event_type"] for v in event_types.values()]
    seen_counts: Dict[str,int] = {}

    # quick index of name -> matched rules
    matched: Dict[str, List[Rule]] = {n: match_rules(rules, n) for n in names}

    age_max = rng.choices(age_max_dist, weights=age_max_w, k=1)[0]

    # track which prereqs are satisfied: any event’s occurrence satisfies itself
    occurred = set()

    # sample a random target number of events: 2 - max_events
    target_events = rng.randint(2, max_events)
    
    for age in range(age_max+1):
        if len(g.nodes) >= target_events:
            break
        
        # collect candidates allowed by age, prereqs, and caps
        candidates=[]
        for name in names:
            rs = matched[name]
            if not allowed_by_age(rs, age): 
                continue
            reqs = prereqs_for(rs)
            if any(req not in occurred for req in reqs):
                continue
            cap = max_count_for(rs)
            if cap is not None and seen_counts.get(name,0) >= cap:
                continue
            p = base_rate_for_age(rs, age, default_rate)
            if p > 0.0:
                candidates.append((name, p))

        # Bernoulli per candidate, then sort by probability to stabilize density
        rng.shuffle(candidates)
        fired=[]
        for name, p in candidates:
            if rng.random() < p:
                fired.append(name)

        # optional: enforce at most K events per age to keep chains reasonable
        K = 3
        if len(fired) > K:
            fired = rng.sample(fired, K)

        # append fired events in deterministic order (by name) to make runs reproducible
        for name in sorted(fired):
            # pass current age and RNG so attributes get sampled per event
            last = add_event(g, name, last, age=age, rng=rng)
            occurred.add(name)
            seen_counts[name] = seen_counts.get(name,0) + 1

    return g

def generate_noise_graphs(n: int, max_events: int=80, rules_json_path: Optional[str]=None, seed: int=1337) -> List[EventGraph]:
    rng = random.Random(seed)
    # empty rules if none provided
    rules = compile_rules(json.load(open(rules_json_path))) if rules_json_path else []
    return [sample_graph(rng, max_events, rules) for _ in range(n)]

# ---------- Example usage ----------
if __name__ == "__main__":
    # python sampler.py (uses no rules) or supply a rules file
    RULES_PATH = Path(__file__).parent / "lib" / "sampling_rules.json"
    graphs = generate_noise_graphs(5, rules_json_path=RULES_PATH, seed=42)
    graphs[0].visualize()
