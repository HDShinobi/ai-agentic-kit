---
name: game-development
description: Game development orchestrator. Routes to platform-specific skills based on project needs. When building games with Unity, Godot, Unreal, Phaser, or any game engine. Routes to platform-specific sub-skills.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Game Development

> **Orchestrator skill** that provides core principles and routes to specialized sub-skills.

---

## When to Use This Skill

You are working on a game development project. This skill teaches the PRINCIPLES of game development and directs you to the right sub-skill based on context.

---

## Sub-Skill Routing

### Platform Selection

| If the game targets... | Use Sub-Skill |
|------------------------|---------------|
| Web browsers (HTML5, WebGL) | `web-games/GUIDE.md` |
| Mobile (iOS, Android) | `mobile-games/GUIDE.md` |
| PC (Steam, Desktop) | `pc-games/GUIDE.md` |
| VR/AR headsets | `vr-ar/GUIDE.md` |

### Dimension Selection

| If the game is... | Use Sub-Skill |
|-------------------|---------------|
| 2D (sprites, tilemaps) | `2d-games/GUIDE.md` |
| 3D (meshes, shaders) | `3d-games/GUIDE.md` |

### Specialty Areas

| If you need... | Use Sub-Skill |
|----------------|---------------|
| GDD, balancing, player psychology | `game-design/GUIDE.md` |
| Multiplayer, networking | `multiplayer/GUIDE.md` |
| Visual style, asset pipeline, animation | `game-art/GUIDE.md` |
| Sound design, music, adaptive audio | `game-audio/GUIDE.md` |

---

## Core Principles (All Platforms)

### 1. The Game Loop

Every game, regardless of platform, follows this pattern:

```
INPUT  → Read player actions
UPDATE → Process game logic (fixed timestep)
RENDER → Draw the frame (interpolated)
```

**Fixed Timestep Rule:**
- Physics/logic: Fixed rate (e.g., 50Hz)
- Rendering: As fast as possible
- Interpolate between states for smooth visuals

---

### 2. Pattern Selection Matrix

| Pattern | Use When | Example |
|---------|----------|---------|
| **State Machine** | 3-5 discrete states | Player: Idle→Walk→Jump |
| **Object Pooling** | Frequent spawn/destroy | Bullets, particles |
| **Observer/Events** | Cross-system communication | Health→UI updates |
| **ECS** | Thousands of similar entities | RTS units, particles |
| **Command** | Undo, replay, networking | Input recording |
| **Behavior Tree** | Complex AI decisions | Enemy AI |

**Decision Rule:** Start with State Machine. Add ECS only when performance demands.

---

### 3. Input Abstraction

Abstract input into ACTIONS, not raw keys:

```
"jump"  → Space, Gamepad A, Touch tap
"move"  → WASD, Left stick, Virtual joystick
```

**Why:** Enables multi-platform, rebindable controls.

---

### 4. Performance Budget (60 FPS = 16.67ms)

| System | Budget |
|--------|--------|
| Input | 1ms |
| Physics | 3ms |
| AI | 2ms |
| Game Logic | 4ms |
| Rendering | 5ms |
| Buffer | 1.67ms |

**Optimization Priority:**
1. Algorithm (O(n²) → O(n log n))
2. Batching (reduce draw calls)
3. Pooling (avoid GC spikes)
4. LOD (detail by distance)
5. Culling (skip invisible)

---

### 5. AI Selection by Complexity

| AI Type | Complexity | Use When |
|---------|------------|----------|
| **FSM** | Simple | 3-5 states, predictable behavior |
| **Behavior Tree** | Medium | Modular, designer-friendly |
| **GOAP** | High | Emergent, planning-based |
| **Utility AI** | High | Scoring-based decisions |

---

### 6. Collision Strategy

| Type | Best For |
|------|----------|
| **AABB** | Rectangles, fast checks |
| **Circle** | Round objects, cheap |
| **Spatial Hash** | Many similar-sized objects |
| **Quadtree** | Large worlds, varying sizes |

---

## Anti-Patterns (Universal)

| Don't | Do |
|-------|-----|
| Update everything every frame | Use events, dirty flags |
| Create objects in hot loops | Object pooling |
| Cache nothing | Cache references |
| Optimize without profiling | Profile first |
| Mix input with logic | Abstract input layer |

---

## Routing Examples

### Example 1: "I want to make a browser-based 2D platformer"
→ Start with `web-games/GUIDE.md` for framework selection
→ Then `2d-games/GUIDE.md` for sprite/tilemap patterns
→ Reference `game-design/GUIDE.md` for level design

### Example 2: "Mobile puzzle game for iOS and Android"
→ Start with `mobile-games/GUIDE.md` for touch input and stores
→ Use `game-design/GUIDE.md` for puzzle balancing

### Example 3: "Multiplayer VR shooter"
→ `vr-ar/GUIDE.md` for comfort and immersion
→ `3d-games/GUIDE.md` for rendering
→ `multiplayer/GUIDE.md` for networking

---

> **Remember:** Great games come from iteration, not perfection. Prototype fast, then polish.
