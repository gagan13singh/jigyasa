"""
physengine.curriculum.derivations
=================================

Complete 40-topic Class 9-12 Physics Derivation & Analytical Solution Suite.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DerivationTopic:
    """Represents a structured physics derivation and analytical model."""

    topic_id: str
    level: int
    level_name: str
    title: str
    key_formula_latex: str
    derivation_steps_latex: list[str]
    description: str


# ── Complete 40-Topic Catalog ───────────────────────────────────────────────

CURRICULUM_TOPICS: dict[str, DerivationTopic] = {
    # ── Level 1: Fundamental Mechanics ──
    "newton_second_law": DerivationTopic(
        topic_id="newton_second_law",
        level=1,
        level_name="Fundamental Mechanics",
        title="Newton's Second Law of Motion",
        key_formula_latex=r"\vec{F} = m\vec{a}",
        derivation_steps_latex=[
            r"\vec{p} = m\vec{v} \quad \text{(Linear Momentum)}",
            r"\vec{F} = \frac{d\vec{p}}{dt} = \frac{d(m\vec{v})}{dt}",
            r"\vec{F} = m\frac{d\vec{v}}{dt} = m\vec{a}",
        ],
        description="Relates applied net force to rate of change of momentum and acceleration.",
    ),
    "impulse_momentum": DerivationTopic(
        topic_id="impulse_momentum",
        level=1,
        level_name="Fundamental Mechanics",
        title="Impulse–Momentum Theorem",
        key_formula_latex=r"\vec{J} = \int \vec{F}\,dt = \Delta\vec{p}",
        derivation_steps_latex=[
            r"\vec{J} = \int_{t_1}^{t_2} \vec{F}\,dt \quad \text{(Definition)}",
            r"\vec{F} = \frac{d\vec{p}}{dt} \implies \vec{F}\,dt = d\vec{p}",
            r"\vec{J} = \int_{\vec{p}_1}^{\vec{p}_2} d\vec{p} = \Delta\vec{p}",
        ],
        description="Impulse equals the area under the Force-Time curve and change in momentum.",
    ),
    "momentum_conservation": DerivationTopic(
        topic_id="momentum_conservation",
        level=1,
        level_name="Fundamental Mechanics",
        title="Conservation of Linear Momentum",
        key_formula_latex=r"\vec{p}_1 + \vec{p}_2 = \text{constant}",
        derivation_steps_latex=[
            r"\vec{F}_{12} = -\vec{F}_{21} \quad \text{(Newton's Third Law)}",
            r"\frac{d\vec{p}_1}{dt} = -\frac{d\vec{p}_2}{dt}",
            r"\frac{d}{dt}(\vec{p}_1 + \vec{p}_2) = 0 \implies \Sigma\vec{p} = \text{const}",
        ],
        description="In an isolated system with no external force, linear momentum is conserved.",
    ),
    "equations_of_motion": DerivationTopic(
        topic_id="equations_of_motion",
        level=1,
        level_name="Fundamental Mechanics",
        title="Four Kinematic Equations of Motion",
        key_formula_latex=r"v = u + at, \quad s = ut + \frac{1}{2}at^2, \quad v^2 = u^2 + 2as",
        derivation_steps_latex=[
            r"a = \frac{dv}{dt} \implies \int_u^v dv = \int_0^t a\,dt \implies v = u + at",
            r"v = \frac{ds}{dt} = u + at \implies s = ut + \frac{1}{2}at^2",
            r"a = v\frac{dv}{ds} \implies \int_0^s a\,ds = \int_u^v v\,dv \implies v^2 = u^2 + 2as",
            r"s = \frac{u + v}{2}t \quad \text{(Average velocity relation)}",
        ],
        description="Fundamental equations for uniformly accelerated motion derived via calculus.",
    ),
    "newton_third_law": DerivationTopic(
        topic_id="newton_third_law",
        level=1,
        level_name="Fundamental Mechanics",
        title="Newton's Third Law (Action-Reaction)",
        key_formula_latex=r"\vec{F}_{12} = -\vec{F}_{21}, \quad |\vec{F}_{12}| = |\vec{F}_{21}|",
        derivation_steps_latex=[
            r"\text{To every action, there is an equal and opposite reaction.}",
            r"\vec{F}_{AB} = -\vec{F}_{BA}",
            r"\text{Action and reaction act on two different bodies simultaneously.}",
        ],
        description="Mutual forces between interacting bodies are equal and opposite.",
    ),

    # ── Level 2: Friction & Incline Mechanics ──
    "static_friction": DerivationTopic(
        topic_id="static_friction",
        level=2,
        level_name="Friction & Inclines",
        title="Limiting Static Friction",
        key_formula_latex=r"f_s \le f_{\max} = \mu_s N = \mu_s mg",
        derivation_steps_latex=[
            r"f_s \le f_{\max} \quad \text{(Self-adjusting static friction)}",
            r"f_{\max} = \mu_s N",
            r"\text{Horizontal surface: } N = mg \implies f_{\max} = \mu_s mg",
        ],
        description="Static friction matches applied force until reaching limiting maximum.",
    ),
    "kinetic_friction": DerivationTopic(
        topic_id="kinetic_friction",
        level=2,
        level_name="Friction & Inclines",
        title="Kinetic Friction",
        key_formula_latex=r"f_k = \mu_k N = \mu_k mg",
        derivation_steps_latex=[
            r"\text{Once sliding begins, friction drops to kinetic value } f_k.",
            r"f_k = \mu_k N \quad (\mu_k < \mu_s)",
            r"\text{On horizontal floor: } f_k = \mu_k mg",
        ],
        description="Kinetic friction opposes relative sliding motion between surfaces.",
    ),
    "angle_of_friction": DerivationTopic(
        topic_id="angle_of_friction",
        level=2,
        level_name="Friction & Inclines",
        title="Angle of Friction (λ)",
        key_formula_latex=r"\tan\lambda = \mu_s",
        derivation_steps_latex=[
            r"\text{Resultant reaction } \vec{R} = \vec{N} + \vec{f}_s",
            r"\tan\lambda = \frac{f_{\max}}{N} = \frac{\mu_s N}{N} = \mu_s",
            r"\therefore \lambda = \tan^{-1}(\mu_s)",
        ],
        description="Angle resultant contact force makes with normal at limiting equilibrium.",
    ),
    "angle_of_repose": DerivationTopic(
        topic_id="angle_of_repose",
        level=2,
        level_name="Friction & Inclines",
        title="Angle of Repose (θ_r)",
        key_formula_latex=r"\tan\theta_r = \mu_s \implies \theta_r = \lambda",
        derivation_steps_latex=[
            r"\text{Down-plane gravity: } mg\sin\theta",
            r"\text{Limiting friction: } f_{\max} = \mu_s mg\cos\theta",
            r"mg\sin\theta = \mu_s mg\cos\theta \implies \tan\theta_r = \mu_s",
            r"\therefore \theta_r = \lambda \quad (\text{Angle of Repose = Angle of Friction})",
        ],
        description="Maximum angle of inclined plane at which a resting body does not slip.",
    ),
    "incline_acceleration": DerivationTopic(
        topic_id="incline_acceleration",
        level=2,
        level_name="Friction & Inclines",
        title="Acceleration on Inclined Plane",
        key_formula_latex=r"a = g(\sin\theta - \mu_k \cos\theta)",
        derivation_steps_latex=[
            r"\Sigma F_{\parallel} = mg\sin\theta - f_k = ma",
            r"f_k = \mu_k N = \mu_k mg\cos\theta",
            r"mg\sin\theta - \mu_k mg\cos\theta = ma \implies a = g(\sin\theta - \mu_k\cos\theta)",
        ],
        description="Net downward acceleration of a block sliding on an incline with friction.",
    ),
    "pull_horizontal": DerivationTopic(
        topic_id="pull_horizontal",
        level=2,
        level_name="Friction & Inclines",
        title="Block Pulled Horizontally",
        key_formula_latex=r"a = \frac{F - \mu_k mg}{m}",
        derivation_steps_latex=[
            r"F_{\text{net}} = F - f_k = ma",
            r"f_k = \mu_k mg",
            r"a = \frac{F - \mu_k mg}{m}",
        ],
        description="Acceleration of a block on a rough horizontal floor under external pull.",
    ),
    "pull_angle": DerivationTopic(
        topic_id="pull_angle",
        level=2,
        level_name="Friction & Inclines",
        title="Block Pulled at an Angle (θ)",
        key_formula_latex=r"a = \frac{F\cos\theta - \mu_k(mg - F\sin\theta)}{m}",
        derivation_steps_latex=[
            r"N + F\sin\theta = mg \implies N = mg - F\sin\theta",
            r"f_k = \mu_k(mg - F\sin\theta)",
            r"F\cos\theta - f_k = ma \implies a = \frac{F\cos\theta - \mu_k(mg - F\sin\theta)}{m}",
        ],
        description="Pulling at an upward angle reduces the normal force and friction.",
    ),
    "min_pull_force": DerivationTopic(
        topic_id="min_pull_force",
        level=2,
        level_name="Friction & Inclines",
        title="Minimum Force Required to Move a Block",
        key_formula_latex=r"F_{\min} = \frac{\mu_s mg}{\sqrt{1 + \mu_s^2}} = mg\sin\lambda",
        derivation_steps_latex=[
            r"F(\cos\theta + \mu_s\sin\theta) = \mu_s mg",
            r"F = \frac{\mu_s mg}{\cos\theta + \mu_s\sin\theta}",
            r"F_{\min} = \frac{\mu_s mg}{\sqrt{1+\mu_s^2}} \quad (\theta = \tan^{-1}\mu_s)",
        ],
        description="Calculates the least pulling force needed to move a resting block.",
    ),
    "optimum_pull_angle": DerivationTopic(
        topic_id="optimum_pull_angle",
        level=2,
        level_name="Friction & Inclines",
        title="Optimum Angle for Minimum Pulling Force",
        key_formula_latex=r"\theta_{\text{opt}} = \tan^{-1}(\mu_s) = \lambda",
        derivation_steps_latex=[
            r"\frac{d}{d\theta}(\cos\theta + \mu_s\sin\theta) = -\sin\theta + \mu_s\cos\theta = 0",
            r"\tan\theta = \mu_s \implies \theta_{\text{opt}} = \tan^{-1}\mu_s = \lambda",
        ],
        description="Proves the optimum pulling angle equals the angle of friction.",
    ),

    # ── Level 3: Circular Motion & Banking ──
    "centripetal_force": DerivationTopic(
        topic_id="centripetal_force",
        level=3,
        level_name="Circular Motion",
        title="Centripetal Acceleration & Force",
        key_formula_latex=r"a_c = \frac{v^2}{r} = \omega^2 r, \quad F_c = \frac{mv^2}{r}",
        derivation_steps_latex=[
            r"\vec{r}(t) = r\cos(\omega t)\hat{i} + r\sin(\omega t)\hat{j}",
            r"\vec{a}(t) = -\omega^2\vec{r} \implies a_c = \omega^2 r = \frac{v^2}{r}",
            r"F_c = ma_c = \frac{mv^2}{r}",
        ],
        description="Derivation of centripetal acceleration vector directed toward circle center.",
    ),
    "banking_no_friction": DerivationTopic(
        topic_id="banking_no_friction",
        level=3,
        level_name="Circular Motion",
        title="Banking of Roads (Frictionless)",
        key_formula_latex=r"\tan\theta = \frac{v^2}{rg} \implies v = \sqrt{rg\tan\theta}",
        derivation_steps_latex=[
            r"N\sin\theta = \frac{mv^2}{r}, \quad N\cos\theta = mg",
            r"\tan\theta = \frac{v^2}{rg} \implies v = \sqrt{rg\tan\theta}",
        ],
        description="Optimum design speed where normal reaction provides centripetal force.",
    ),
    "banking_with_friction": DerivationTopic(
        topic_id="banking_with_friction",
        level=3,
        level_name="Circular Motion",
        title="Banking with Friction (v_max & v_min)",
        key_formula_latex=r"v_{\max} = \sqrt{rg\frac{\tan\theta + \mu}{1 - \mu\tan\theta}}",
        derivation_steps_latex=[
            r"N\sin\theta + f_s\cos\theta = \frac{mv^2}{r}, \quad N\cos\theta - f_s\sin\theta = mg",
            r"f_s = \mu N \implies v_{\max} = \sqrt{rg\frac{\tan\theta + \mu}{1 - \mu\tan\theta}}",
            r"v_{\min} = \sqrt{rg\frac{\tan\theta - \mu}{1 + \mu\tan\theta}}",
        ],
        description="Safe velocity range on a banked curve accounting for lateral friction.",
    ),
    "vertical_circle_tension": DerivationTopic(
        topic_id="vertical_circle_tension",
        level=3,
        level_name="Circular Motion",
        title="Tension in Vertical Circular Motion",
        key_formula_latex=r"T_{\text{bot}} = mg + \frac{mv^2}{r}",
        derivation_steps_latex=[
            r"\text{At bottom: } T_b - mg = \frac{mv_b^2}{r} \implies T_b = mg + \frac{mv_b^2}{r}",
            r"\text{At top: } T_t + mg = \frac{mv_t^2}{r} \implies T_t = \frac{mv_t^2}{r} - mg",
        ],
        description="Calculates string/track tension throughout a vertical circle.",
    ),
    "vertical_circle_critical": DerivationTopic(
        topic_id="vertical_circle_critical",
        level=3,
        level_name="Circular Motion",
        title="Minimum Speed for Complete Vertical Circle",
        key_formula_latex=r"v_{\text{bottom}} = \sqrt{5gr}, \quad v_{\text{top}} = \sqrt{gr}",
        derivation_steps_latex=[
            r"T_{\text{top}} = 0 \implies v_{\text{top}} = \sqrt{gr}",
            r"\frac{1}{2}mv_b^2 = \frac{1}{2}mv_t^2 + 2mgr \implies v_b = \sqrt{5gr}",
        ],
        description="Minimum entry velocity required to complete a vertical loop without slacking.",
    ),

    # ── Level 4: Work, Energy & Power ──
    "work_constant_force": DerivationTopic(
        topic_id="work_constant_force",
        level=4,
        level_name="Work, Energy & Power",
        title="Work Done by Constant Force",
        key_formula_latex=r"W = \vec{F}\cdot\vec{s} = Fs\cos\theta",
        derivation_steps_latex=[
            r"W = \vec{F}\cdot\vec{s} = Fs\cos\theta",
            r"\theta = 0^\circ \implies W = +Fs \quad (\text{Positive Work})",
            r"\theta = 90^\circ \implies W = 0 \quad (\text{Zero Work})",
            r"\theta = 180^\circ \implies W = -Fs \quad (\text{Negative Work})",
        ],
        description="Definition of mechanical work as dot product of force and displacement.",
    ),
    "work_variable_force": DerivationTopic(
        topic_id="work_variable_force",
        level=4,
        level_name="Work, Energy & Power",
        title="Work Done by Variable Force",
        key_formula_latex=r"W = \int_{x_1}^{x_2} F(x)\,dx = \text{Area under } F-x \text{ curve}",
        derivation_steps_latex=[
            r"dW = F(x)\,dx",
            r"W = \int_{x_1}^{x_2} F(x)\,dx = \text{Area under } F(x) \text{ curve}",
        ],
        description="Integration of position-dependent force represented by F-x curve area.",
    ),
    "work_energy_theorem": DerivationTopic(
        topic_id="work_energy_theorem",
        level=4,
        level_name="Work, Energy & Power",
        title="Work–Energy Theorem",
        key_formula_latex=r"W_{\text{net}} = \Delta K = \frac{1}{2}mv^2 - \frac{1}{2}mu^2",
        derivation_steps_latex=[
            r"F = mv\frac{dv}{dx} \implies F\,dx = mv\,dv",
            r"W = \int_u^v mv\,dv = \frac{1}{2}mv^2 - \frac{1}{2}mu^2 = \Delta K",
        ],
        description="Net work done on a particle equals change in its kinetic energy.",
    ),
    "kinetic_energy": DerivationTopic(
        topic_id="kinetic_energy",
        level=4,
        level_name="Work, Energy & Power",
        title="Kinetic Energy Derivation",
        key_formula_latex=r"K = \frac{1}{2}mv^2",
        derivation_steps_latex=[
            r"W = (ma)s, \quad v^2 = 2as \implies as = \frac{1}{2}v^2",
            r"K = W = \frac{1}{2}mv^2",
        ],
        description="Energy possessed by a body by virtue of its velocity.",
    ),
    "gravitational_pe": DerivationTopic(
        topic_id="gravitational_pe",
        level=4,
        level_name="Work, Energy & Power",
        title="Gravitational Potential Energy",
        key_formula_latex=r"U = mgh",
        derivation_steps_latex=[
            r"W = \int_0^h mg\,dy = mgh",
            r"\therefore U(h) = mgh",
        ],
        description="Potential energy stored in gravitational field at height h.",
    ),
    "mechanical_energy_conservation": DerivationTopic(
        topic_id="mechanical_energy_conservation",
        level=4,
        level_name="Work, Energy & Power",
        title="Conservation of Mechanical Energy",
        key_formula_latex=r"E_{\text{total}} = K + U = \text{constant}",
        derivation_steps_latex=[
            r"W_c = -\Delta U, \quad W_c = \Delta K",
            r"\Delta K = -\Delta U \implies \Delta(K + U) = 0 \implies K + U = \text{constant}",
        ],
        description="Total mechanical energy remains constant in conservative field.",
    ),
    "spring_pe": DerivationTopic(
        topic_id="spring_pe",
        level=4,
        level_name="Work, Energy & Power",
        title="Potential Energy of a Spring",
        key_formula_latex=r"U = \frac{1}{2}kx^2",
        derivation_steps_latex=[
            r"F_{\text{ext}} = +kx",
            r"W = \int_0^x kx'\,dx' = \frac{1}{2}kx^2 \implies U_{\text{spring}} = \frac{1}{2}kx^2",
        ],
        description="Elastic potential energy stored in an elongated or compressed spring.",
    ),
    "spring_work": DerivationTopic(
        topic_id="spring_work",
        level=4,
        level_name="Work, Energy & Power",
        title="Work Done by Spring",
        key_formula_latex=r"W_{\text{spring}} = -\frac{1}{2}k(x_2^2 - x_1^2)",
        derivation_steps_latex=[
            r"dW = F_{\text{spring}}\,dx = -kx\,dx",
            r"W_{\text{spring}} = \int_{x_1}^{x_2} (-kx)\,dx = -\frac{1}{2}k(x_2^2 - x_1^2)",
        ],
        description="Work performed by restoring spring force during displacement.",
    ),
    "power": DerivationTopic(
        topic_id="power",
        level=4,
        level_name="Work, Energy & Power",
        title="Power (Average & Instantaneous)",
        key_formula_latex=r"P = \frac{dW}{dt} = \vec{F}\cdot\vec{v} = Fv\cos\theta",
        derivation_steps_latex=[
            r"P_{\text{avg}} = \frac{\Delta W}{\Delta t}",
            r"P_{\text{inst}} = \frac{dW}{dt} = \vec{F}\cdot\vec{v}",
        ],
        description="Rate at which mechanical work is performed by a force.",
    ),

    # ── Level 5: Collisions & Restitution ──
    "elastic_collision_1d": DerivationTopic(
        topic_id="elastic_collision_1d",
        level=5,
        level_name="Collisions",
        title="1D Elastic Collision Velocities",
        key_formula_latex=r"v_1 = \frac{m_1-m_2}{m_1+m_2}u_1 + \frac{2m_2}{m_1+m_2}u_2",
        derivation_steps_latex=[
            r"m_1 u_1 + m_2 u_2 = m_1 v_1 + m_2 v_2",
            r"v_1 = \frac{m_1-m_2}{m_1+m_2}u_1 + \frac{2m_2}{m_1+m_2}u_2",
        ],
        description="Exact velocity exchange equations in a 1D elastic collision.",
    ),
    "coefficient_of_restitution": DerivationTopic(
        topic_id="coefficient_of_restitution",
        level=5,
        level_name="Collisions",
        title="Coefficient of Restitution (e)",
        key_formula_latex=r"e = \frac{v_2 - v_1}{u_1 - u_2}",
        derivation_steps_latex=[
            r"e = \frac{v_2 - v_1}{u_1 - u_2} = \frac{v_{\text{sep}}}{v_{\text{app}}}",
            r"e = 1 \implies \text{Elastic}, \quad e = 0 \implies \text{Perfect Inelastic}",
        ],
        description="Dimensionless ratio determining collision elasticity.",
    ),
    "perfectly_inelastic": DerivationTopic(
        topic_id="perfectly_inelastic",
        level=5,
        level_name="Collisions",
        title="Perfectly Inelastic Collision",
        key_formula_latex=r"v_{\text{common}} = \frac{m_1 u_1 + m_2 u_2}{m_1 + m_2}",
        derivation_steps_latex=[
            r"m_1 u_1 + m_2 u_2 = (m_1 + m_2)v",
            r"v = \frac{m_1 u_1 + m_2 u_2}{m_1 + m_2}",
        ],
        description="Common velocity when colliding masses coalesce and move together.",
    ),
    "kinetic_energy_loss": DerivationTopic(
        topic_id="kinetic_energy_loss",
        level=5,
        level_name="Collisions",
        title="Loss of Kinetic Energy in Inelastic Collision",
        key_formula_latex=r"\Delta K = \frac{1}{2}\frac{m_1 m_2}{m_1 + m_2}(u_1 - u_2)^2",
        derivation_steps_latex=[
            r"K_i = \frac{1}{2}m_1 u_1^2 + \frac{1}{2}m_2 u_2^2",
            r"K_f = \frac{1}{2}(m_1 + m_2)v^2",
            r"\Delta K = K_i - K_f = \frac{1}{2}\frac{m_1 m_2}{m_1 + m_2}(u_1 - u_2)^2",
        ],
        description="Mechanical kinetic energy transformed into heat and deformation.",
    ),
    "wall_collision": DerivationTopic(
        topic_id="wall_collision",
        level=5,
        level_name="Collisions",
        title="Collision with a Fixed Wall",
        key_formula_latex=r"v = -e u",
        derivation_steps_latex=[
            r"\lim_{m_2\to\infty} \left[\frac{m_1-m_2}{m_1+m_2}u_1\right] = -u_1",
            r"\text{With restitution } e: v = -e u",
        ],
        description="Rebound velocity when a moving particle strikes a massive wall.",
    ),

    # ── Level 6: Projectile Motion ──
    "projectile_range": DerivationTopic(
        topic_id="projectile_range",
        level=6,
        level_name="Projectile Motion",
        title="Horizontal Range of Projectile",
        key_formula_latex=r"R = \frac{u^2 \sin(2\theta)}{g}",
        derivation_steps_latex=[
            r"x(t) = (u\cos\theta)t, \quad T = \frac{2u\sin\theta}{g}",
            r"R = u\cos\theta\left(\frac{2u\sin\theta}{g}\right) = \frac{u^2\sin(2\theta)}{g}",
        ],
        description="Total horizontal distance traveled by projectile.",
    ),
    "projectile_max_height": DerivationTopic(
        topic_id="projectile_max_height",
        level=6,
        level_name="Projectile Motion",
        title="Maximum Height of Projectile",
        key_formula_latex=r"H_{\max} = \frac{u^2 \sin^2\theta}{2g}",
        derivation_steps_latex=[
            r"v_y = 0 \implies 0 = (u\sin\theta)^2 - 2gH",
            r"H_{\max} = \frac{u^2\sin^2\theta}{2g}",
        ],
        description="Peak vertical displacement achieved during flight.",
    ),
    "projectile_time_of_flight": DerivationTopic(
        topic_id="projectile_time_of_flight",
        level=6,
        level_name="Projectile Motion",
        title="Time of Flight",
        key_formula_latex=r"T = \frac{2u\sin\theta}{g}",
        derivation_steps_latex=[
            r"y(t) = (u\sin\theta)t - \frac{1}{2}gt^2 = 0",
            r"t\left(u\sin\theta - \frac{1}{2}gt\right) = 0 \implies T = \frac{2u\sin\theta}{g}",
        ],
        description="Total elapsed time from launch to ground impact.",
    ),
    "projectile_trajectory": DerivationTopic(
        topic_id="projectile_trajectory",
        level=6,
        level_name="Projectile Motion",
        title="Equation of Trajectory (Parabola)",
        key_formula_latex=r"y = x\tan\theta - \frac{gx^2}{2u^2\cos^2\theta}",
        derivation_steps_latex=[
            r"t = \frac{x}{u\cos\theta}",
            r"y = (u\sin\theta)t - \frac{1}{2}gt^2 = x\tan\theta - \frac{gx^2}{2u^2\cos^2\theta}",
        ],
        description="Algebraic relation proving parabolic trajectory.",
    ),
    "projectile_max_range": DerivationTopic(
        topic_id="projectile_max_range",
        level=6,
        level_name="Projectile Motion",
        title="Maximum Range Condition (θ = 45°)",
        key_formula_latex=r"\theta = 45^\circ \implies R_{\max} = \frac{u^2}{g}",
        derivation_steps_latex=[
            r"\sin(2\theta) = 1 \implies 2\theta = 90^\circ \implies \theta = 45^\circ",
            r"R_{\max} = \frac{u^2}{g}",
        ],
        description="Demonstrates why 45 degrees yields the greatest range.",
    ),
    "projectile_complementary": DerivationTopic(
        topic_id="projectile_complementary",
        level=6,
        level_name="Projectile Motion",
        title="Complementary Angles Property",
        key_formula_latex=r"R_\theta = R_{90^\circ - \theta}",
        derivation_steps_latex=[
            r"R(\theta) = \frac{u^2\sin(2\theta)}{g}",
            r"R(90^\circ - \theta) = \frac{u^2\sin(180^\circ - 2\theta)}{g} = R(\theta)",
        ],
        description="Two projectiles fired at complementary angles achieve the exact same range.",
    ),
}
