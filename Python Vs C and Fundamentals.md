# Programming Paradigms & Python Fundamentals

## 1. Paradigms & Languages: Theoretical Overview

### Structured vs. Object-Oriented Programming (OOP)

- **Structured (Procedural) Programming:** Organizes software around step-by-step algorithms, routines, and functions operating on separate, passive data structures (e.g., `struct`s in C).
- **Object-Oriented Programming (OOP):** Organizes software around autonomous **objects** that unify state (attributes) and behavior (methods), protecting data via **encapsulation**.

| Criterion | Structured Programming | Object-Oriented Programming (OOP) |
|---|---|---|
| **Approach** | Action-centered: "Which functions need to execute?" | Entity-centered: "Which objects interact with each other?" |
| **Data & Functions** | Decoupled. Functions access and mutate data directly. | Unified inside the same object (encapsulation). |
| **Global State** | Relies on shared global variables, leading to side effects. | Encapsulated within object instances. |
| **Data Integrity** | Business logic validation is distributed across all system functions. | Validation is centralized within the object managing its state. |
| **Code Reuse** | Function duplicates ("endless clones") for specific data variants. | Inheritance and polymorphism extend existing behaviors cleanly. |

### The Three Core Problems of Structured Programming (Topic 2)

*Based on Topic 2 course materials (Prof. Leonel Morgado).*

1. **Side effects of global state:** Unintended mutations of shared global variables by independent functions make execution flow unpredictable (e.g., the 1996 Ariane 5 rocket failure).
2. **"Endless clones" (code reuse issues):** Multiple similar functions created to sort or manipulate the same data structures independently can violate internal state assumptions made by other functions.
3. **Data inconsistency & fragility:** Without encapsulation, any function can insert invalid values (e.g., negative ages, arbitrary letters appended to phone numbers) without validation at the source.

### Execution Models: C vs. Python

- **C (native compilation):**
  - Translates source code into machine-specific binary code (x86, ARM).
  - Provides maximum hardware performance and direct memory access.
  - Requires recompilation for different operating systems or target CPUs.
- **Python (bytecode + PVM):**
  - Translates `.py` source files into intermediate **bytecode**, executed by the **Python Virtual Machine (PVM)**.
  - Offers cross-platform portability across hardware architectures.

---

## 2. Practical Case Study: GreenTrack (C Architecture Analysis)

An analysis of a multi-module C project (`main.c`, `plants.c`, `tasks.c`, `watering.c`, `data.c`) demonstrates the strengths and limits of **modular structured programming**:

```c
/* plants.c - Module-level static state encapsulation */
#include "../include/plants.h"
#include "../include/types.h"

static Plant plants[MAX_PLANTS];
static int total_plants = 0;

int add_plant(char *name, char *species, char *planting_date, int interval) {
    if (total_plants >= MAX_PLANTS || name == NULL) return 0;

    plants[total_plants].id = total_plants + 1;
    strncpy(plants[total_plants].name, name, sizeof(plants[total_plants].name) - 1);
    plants[total_plants].watering_interval = interval;
    plants[total_plants].last_watering = 0;

    total_plants++;
    return 1;
}
```

### Architectural Breakdown

- **Data/function separation:** Entities (`Plant`, `Task`, `Watering`) are passive `struct` definitions, while functions in `.c` files act as procedural manipulators.
- **File-level scope control:** Uses `static` arrays to hide module state, avoiding uncontrolled global variables while maintaining a procedural state model.
- **Top-down control flow:** Execution is driven by a main loop (`main.c`) invoking explicit procedures sequentially.
- **Manual referential integrity:** Foreign key checks (e.g., ensuring a `plant_id` exists before registering a watering) must be manually enforced inside each individual procedure.

---

## 3. Python Fundamentals for C / TypeScript Developers

### A) Dynamic Typing

In Python, types belong to **values** (objects in memory), not variables. Variables act as pointers/references to memory locations.

```python
# C: int age = 20; (Static / Fixed type)
# Python: Dynamic typing (No explicit type keywords)
age = 20        # Inferred as 'int'
age = "Twenty"  # Re-assigned to point to a 'str' object
```

**Using type hints (TypeScript style):** Type annotations preserve editor autocompletion and static analysis without altering runtime dynamics.

```python
def calculate_area(width: float, height: float) -> float:
    return width * height

name: str = "GreenTrack"
```

### B) Automatic Memory Management

Python eliminates explicit `malloc()` and `free()` calls through two runtime mechanisms:

- **Reference counting:** Deallocates memory immediately when an object's reference counter drops to zero.
- **Garbage collector (GC):** Periodically runs in the background to detect and clean up circular reference deadlocks.

```python
# Reference Copy vs. Data Copy
a = [1, 2, 3]
b = a        # Both variables reference the SAME memory location!
b.append(4)  # Modifies both 'a' and 'b'

c = a.copy() # Creates an independent memory duplicate
```

### C) Core Python Data Structures

```python
# 1. List (Dynamic ordered array)
fruits = ["apple", "banana", "orange"]
fruits.append("grape")

# 2. Dictionary (Key-Value / Hash Map)
plant = {
    "id": 1,
    "name": "Monstera",
    "watering_interval": 7
}

# 3. Tuple (Immutable collection)
coordinates = (38.7071, -9.1355)

# 4. Set (Unordered collection of unique items)
unique_ids = {101, 102, 103}
```

### D) Control Flow Syntax Comparison

```python
# For loop with range (Equivalent to for(int i=0; i<5; i++) in C)
for i in range(5):
    print(f"Index: {i}")

# Foreach iteration over elements
for fruit in fruits:
    print(fruit)

# Conditional branching
if age >= 18:
    print("Adult")
elif age > 12:
    print("Teenager")
else:
    print("Child")
```
