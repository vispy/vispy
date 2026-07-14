.. title:: VisPy | Scientific visualization from plots to applications

.. raw:: html

   <div class="vispy-home">
     <header class="home-hero">
       <video class="home-hero__media" autoplay muted loop playsinline preload="metadata" poster="_static/landing/datoviz-textured-planet.webp" aria-hidden="true">
         <source src="_static/landing/datoviz-textured-planet.mp4" type="video/mp4">
       </video>
       <div class="home-hero__content">
         <p class="home-kicker">GPU visualization for Python</p>
         <h1>VisPy</h1>
         <p class="home-hero__offer">Fast, interactive scientific visualization in Python.</p>
         <p class="home-hero__summary">Create plots, explore large datasets, and build complete scientific applications with open-source tools.</p>
         <div class="home-actions" aria-label="Primary links">
           <a class="home-button home-button--primary" href="vispy.html">Read the VisPy docs</a>
         </div>
         <p class="home-status-note"><strong>Current status</strong><span>VisPy is stable.</span><span>Datoviz is the standalone GPU engine and flagship interactive backend for the developing VisPy 2 architecture.</span><span>VisPy 2 and GSP are still experimental.</span></p>
       </div>
       <p class="home-hero__caption">NASA Blue Marble Earth rendered as a textured mesh with Datoviz.</p>
     </header>

     <main>
       <section class="home-section home-section--intro" aria-labelledby="available-title">
         <div class="home-section__heading">
           <p class="home-kicker">Available today</p>
           <h2 id="available-title">Use VisPy today. Explore what comes next.</h2>
           <p>Choose VisPy for its stable higher-level Python API, notebooks, and existing applications. Choose Datoviz for modern GPU rendering, large interactive scenes, native integration, or early access to the VisPy 2 rendering direction.</p>
         </div>
         <div class="home-projects">
           <article class="home-project">
             <div><span class="home-badge home-badge--stable">Established</span></div>
             <h3>VisPy</h3>
             <p>The stable, higher-level OpenGL-based Python library for fast, interactive 2D and 3D visualization.</p>
             <ul class="home-project__facts">
               <li>13+ years of open-source development</li>
               <li>Established scientific Python community</li>
               <li>Higher-level APIs across desktop and notebooks</li>
             </ul>
             <a class="home-text-link" href="vispy.html">Documentation and installation <span aria-hidden="true">&#8594;</span></a>
           </article>
           <article class="home-project">
             <div><span class="home-badge home-badge--prerelease">Release candidate</span></div>
             <h3>Datoviz</h3>
             <p>The standalone Vulkan-based GPU engine and flagship interactive backend for VisPy 2, available directly today.</p>
             <ul class="home-project__facts">
               <li>Native C and NumPy-aware Python APIs</li>
               <li>Desktop Vulkan and experimental browser WebGPU</li>
               <li>Extensive documentation and 100+ code examples</li>
             </ul>
             <a class="home-text-link" href="https://datoviz.org/">Documentation and examples <span aria-hidden="true">&#8594;</span></a>
           </article>
         </div>
       </section>

       <section class="home-section home-section--dark" aria-labelledby="outputs-title">
         <div class="home-section__heading">
           <p class="home-kicker">Renderer-independent by design</p>
           <h2 id="outputs-title">Describe a visualization once. Render it where you need it.</h2>
           <p>Think of the experimental Graphics Server Protocol (GSP) as a common language between scientific Python code and rendering engines. Your code describes points, images, axes, layouts, and interactions. GSP passes that description to Datoviz, Matplotlib, or another backend to draw it.</p>
           <a class="home-text-link" href="https://github.com/vispy/GSP_API/blob/agentic-gsp-vispy2/whitepaper/gsp-whitepaper.pdf">Read the draft GSP white paper <span aria-hidden="true">&#8594;</span></a>
         </div>
         <div class="home-flow" aria-label="VisPy renderer-independent flow">
           <div class="home-flow__producer"><span>Describe</span><strong>VisPy 2</strong><small>Plots, views, and applications</small></div>
           <div class="home-flow__arrow" aria-hidden="true">&#8594;</div>
           <div class="home-flow__protocol"><span>Exchange</span><strong>GSP</strong><small>Semantic graphics protocol</small></div>
           <div class="home-flow__arrow" aria-hidden="true">&#8594;</div>
           <div class="home-flow__targets">
             <div><strong>Datoviz</strong><small>Interactive GPU</small></div>
             <div><strong>Matplotlib</strong><small>Static and vector</small></div>
             <div><strong>Future backends</strong><small>New platforms</small></div>
           </div>
         </div>
       </section>

       <section class="home-section" aria-labelledby="range-title">
         <div class="home-section__heading home-section__heading--compact">
           <p class="home-kicker">One scientific graphics stack</p>
           <h2 id="range-title">From scientific plots to interactive 3D worlds.</h2>
           <p>These examples are rendered by Datoviz, the GPU engine planned underneath VisPy 2. They show the same foundations at work in precise plotting, geographic data, physical simulation, and volumetric science.</p>
         </div>
         <div class="home-showcase" aria-label="Scientific visualization examples">
           <a class="home-showcase__card" href="https://datoviz.org/examples/gallery/showcases/showcases_scientific_plotting/">
             <img src="_static/landing/datoviz-scientific-plotting.webp" alt="Multi-panel scientific plotting workflow rendered by Datoviz">
             <figcaption><strong>Scientific Plotting Workflow</strong><span>Axes, annotations, legends, and coordinated panels</span></figcaption>
           </a>
           <a class="home-showcase__card" href="https://datoviz.org/examples/gallery/showcases/showcases_choropleth/">
             <img src="_static/landing/datoviz-choropleth.webp" alt="World choropleth map rendered by Datoviz">
             <figcaption><strong>Choropleth</strong><span>Data-driven geographic visualization</span></figcaption>
           </a>
           <a class="home-showcase__card" href="https://datoviz.org/examples/gallery/showcases/showcases_gpu_particle_smoke/">
             <video autoplay muted loop playsinline preload="metadata" poster="_static/landing/datoviz-gpu-particle-smoke.webp" aria-hidden="true">
               <source src="_static/landing/datoviz-gpu-particle-smoke.mp4" type="video/mp4">
             </video>
             <img src="_static/landing/datoviz-gpu-particle-smoke.webp" alt="GPU particle smoke simulation rendered by Datoviz">
             <figcaption><strong>GPU Particle Smoke</strong><span>Compute-driven particles at interactive rates</span></figcaption>
           </a>
           <a class="home-showcase__card" href="https://datoviz.org/examples/gallery/showcases/showcases_brain_volume/">
             <video autoplay muted loop playsinline preload="metadata" poster="_static/landing/datoviz-allen-mouse-brain.webp" aria-hidden="true">
               <source src="_static/landing/datoviz-allen-mouse-brain.mp4" type="video/mp4">
             </video>
             <img src="_static/landing/datoviz-allen-mouse-brain.webp" alt="Allen Mouse Brain volume rendered by Datoviz">
             <figcaption><strong>Allen Mouse Brain</strong><span>Interactive 3D scientific volumes</span></figcaption>
           </a>
         </div>
       </section>

       <section class="home-section home-section--domains" aria-labelledby="domains-title">
         <div class="home-section__heading">
           <p class="home-kicker">Built for many fields</p>
           <h2 id="domains-title">Reusable building blocks for specialized science.</h2>
           <p>Different fields need views and interactions designed for their data. VisPy aims to support community-built components for neuroscience, geoscience, astronomy, microscopy, molecular biology, medical imaging, climate science, engineering, and many other disciplines.</p>
         </div>
         <a class="home-domain-media" href="https://datoviz.org/examples/gallery/showcases/showcases_protein/" aria-label="Open the Datoviz protein visualization example">
           <video autoplay muted loop playsinline preload="metadata" poster="_static/landing/datoviz-protein.webp" aria-hidden="true">
             <source src="_static/landing/datoviz-protein.mp4" type="video/mp4">
           </video>
           <img src="_static/landing/datoviz-protein.webp" alt="Protein structure rendered by Datoviz">
           <span>Protein structure rendered with Datoviz <span aria-hidden="true">&#8594;</span></span>
         </a>
       </section>

       <section class="home-section" aria-labelledby="status-title">
         <div class="home-section__heading home-section__heading--compact">
           <p class="home-kicker">Project status</p>
           <h2 id="status-title">What is ready—and what is still experimental.</h2>
         </div>
         <div class="home-status-table" role="table" aria-label="VisPy ecosystem project maturity">
           <div class="home-status-table__row home-status-table__head" role="row"><span role="columnheader">Component</span><span role="columnheader">Maturity</span><span role="columnheader">Role</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell"><a href="vispy.html">VisPy</a></strong><span role="cell"><span class="home-badge home-badge--stable">Established</span></span><span role="cell">Current OpenGL visualization library</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell"><a href="https://datoviz.org/">Datoviz</a></strong><span role="cell"><span class="home-badge home-badge--prerelease">Release candidate</span></span><span role="cell">High-performance GPU backend</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell"><a href="https://github.com/vispy/GSP_API">GSP</a></strong><span role="cell"><span class="home-badge home-badge--experimental">Experimental</span></span><span role="cell">Renderer-independent protocol</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell"><a href="https://github.com/vispy/GSP_API">VisPy 2</a></strong><span role="cell"><span class="home-badge home-badge--experimental">Experimental</span></span><span role="cell">Successor plotting and application API</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell"><a href="https://datoviz.org/reference/webgpu-subset/">WebGPU</a></strong><span role="cell"><span class="home-badge home-badge--experimental">Experimental</span></span><span role="cell">Browser-based GPU rendering</span></div>
           <div class="home-status-table__row" role="row"><strong role="cell">GUI composition</strong><span role="cell"><span class="home-badge home-badge--development">In development</span></span><span role="cell">Interactive scientific workspaces</span></div>
         </div>
       </section>

       <section class="home-section home-section--history" aria-labelledby="history-title">
         <div class="home-history__copy">
           <p class="home-kicker">Built on more than a decade of work</p>
           <h2 id="history-title">Continuity and renewal</h2>
           <p>Founded in 2013, VisPy grew into a widely used open-source GPU library. Its next chapter keeps that community and experience while adding modern rendering, multiple output formats, and support for complete scientific tools.</p>
         </div>
         <div class="home-support">
           <strong>Open development, sustained support</strong>
           <p>VisPy is a NumFOCUS affiliated project. Its development has been supported by the Chan Zuckerberg Initiative and contributors across the scientific Python community.</p>
           <div class="home-inline-links"><a href="org/CHARTER.html">Organization</a><a href="governance/GOVERNANCE.html">Governance</a><a href="https://numfocus.org/">NumFOCUS</a></div>
         </div>
       </section>

       <section class="home-section home-section--participate" aria-labelledby="participate-title">
         <div>
           <p class="home-kicker">Participate</p>
           <h2 id="participate-title">Help shape scientific visualization.</h2>
           <p>We welcome users, backend developers, scientific-tool authors, and domain communities.</p>
         </div>
         <div class="home-actions">
           <a class="home-button home-button--primary" href="https://github.com/vispy/vispy">Contribute on GitHub</a>
           <a class="home-button home-button--secondary" href="community.html">Join the community</a>
         </div>
       </section>
     </main>
   </div>

.. toctree::
  :hidden:

  VisPy documentation <vispy>
  installation
  getting_started/index
  overview
  gallery/index
  API <api/modules>
  news
  Code of Conduct <https://github.com/vispy/vispy/blob/main/CODE_OF_CONDUCT.md>
