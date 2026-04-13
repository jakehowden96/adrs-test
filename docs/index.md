---
template: home.html
title: Architecture Decision Records
hide:
  - toc
---

<div class="adr-home">
<div class="adr-home-hero">
<h1>Architecture Decision<br><span class="adr-accent">Records</span></h1>
<p class="adr-home-subtitle">The central nervous system of our engineering logic. A living archive documenting the "why" behind our technical evolution, ensuring architectural continuity and tribal knowledge preservation.</p>
</div>
<div class="adr-recently-updated">
<div class="adr-section-header">
<div>
<h2>Recently Updated</h2>
<p class="adr-section-desc">Active architectural decisions across all squads</p>
</div>
</div>
<div class="adr-recent-list">
{{ recently_updated_adrs(limit=5) }}
</div>
</div>
<div class="adr-stats">
<div class="adr-stat-card">
<span class="adr-stat-number">{{ total_decisions() }}</span>
<span class="adr-stat-label">TOTAL DECISIONS</span>
</div>
<div class="adr-stat-card">
<span class="adr-stat-number">{{ active_proposals() }}</span>
<span class="adr-stat-label">ACTIVE PROPOSALS</span>
</div>
</div>
</div>
