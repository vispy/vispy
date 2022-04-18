.. title:: Home

.. raw:: html

   <div id="HomeCarousel" class="carousel slide" data-ride="carousel">
      <ol class="carousel-indicators">
        <li data-target="#HomeCarousel" data-slide-to="0" class="active"></li>
        <li data-target="#HomeCarousel" data-slide-to="1" class=""></li>
        <li data-target="#HomeCarousel" data-slide-to="2" class=""></li>
        <li data-target="#HomeCarousel" data-slide-to="3" class=""></li>
      </ol>

      <div class="carousel-inner">

        <div class="carousel-item active">
          <img src="_static/carousel/galaxy.png" alt="Galaxy" style="width:100%">
          <div class="container">
            <div class="carousel-caption">

              <h1>Spiral galaxy simulation</h1>
              <p> Simulation of a spiral galaxy using the density wave theory.</p>
              <p><a class="btn btn-primary" href="gallery/index.html" role="button">Check it out</a></p>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <img src="_static/carousel/high-frequency.png" alt="High-frequency signal" style="width:100%">
          <div class="container">
            <div class="carousel-caption">
              <h1>High frequency signals</h1>
              <p>GPU multisampled high-frequency signal</p>
              <p><a class="btn btn-primary" href="gallery/index.html" role="button">Browse gallery</a></p>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <img src="_static/carousel/mandelbrot.png" alt="Mandelbrot" style="width:100%">
          <div class="container">
            <div class="carousel-caption">
              <h1>Mandelbrot set</h1>
              <p>GPU computed fractals</p>
              <p><a class="btn btn-primary" href="gallery/index.html" role="button">Show me more</a></p>
            </div>
          </div>
        </div>

        <div class="carousel-item">
          <img src="_static/carousel/signals.png" alt="Signals" style="width:100%">
          <div class="container">
            <div class="carousel-caption">
              <h1>Realtime signals</h1>
              <p>320 signals with 10 000 points each</p>
              <p><a class="btn btn-primary" href="gallery/index.html" role="button">Wow!</a></p>
            </div>
          </div>
        </div>
      </div>

      <a class="carousel-control-prev" href="#HomeCarousel" role="button"
         data-slide="prev">
         <span class="carousel-control-prev-icon glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
         <span class="sr-only">Previous</span>
         </a>

      <a class="carousel-control-next" href="#HomeCarousel" role="button"
         data-slide="next">
         <span class="carousel-control-next-icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
         <span class="sr-only">Next</span>
         </a>

    </div>
    <br>

VisPy is a **high-performance interactive 2D/3D data visualization
library** leveraging the computational power of modern **Graphics
Processing Units (GPUs)** through the **OpenGL** library to display very
large datasets.

.. toctree::
  :caption: Getting VisPy
  :maxdepth: 1

  installation

.. toctree::
  :caption: Learning VisPy
  :maxdepth: 2

  getting_started/index

.. toctree::
  :caption: Additional Help
  :maxdepth: 2

  Documentation <overview>

.. toctree::
  :hidden:

  gallery/index
  API <api/modules>
  news
  Code of Conduct <https://github.com/vispy/vispy/blob/main/CODE_OF_CONDUCT.md>

