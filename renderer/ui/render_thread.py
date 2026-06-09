import time
import numpy as np
import multiprocessing
from PyQt5.QtCore import QThread, pyqtSignal
import config
from renderer.raytracer import init_worker, render_pixel_coord

class RenderThread(QThread):
    """
    Class that runs the render process in a separate thread.
    """
    update_signal = pyqtSignal(np.ndarray, int, int)
    finished_signal = pyqtSignal(np.ndarray)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, width, height, camera, objects, lights):
        super().__init__()
        self.width = width
        self.height = height
        self.camera = camera
        self.objects = objects
        self.lights = lights
        self.img_array = np.zeros((height, width, 3), dtype=np.uint8)
        self.running = True
    
    def run(self):
        config.render_stats["ray_count"] = 0
        config.render_stats["start_time"] = time.time()
        config.render_stats["end_time"] = 0
        config.render_stats["processed_pixels"] = 0
        config.render_stats["total_pixels"] = self.width * self.height

        # Create the worker pool ONCE and reuse it for every row. The scene is
        # shipped to each worker a single time via the pool initializer; per-row
        # tasks then carry only (x, y) coordinates. Passing the scene in every
        # task tuple re-pickles the whole scene (incl. large mesh BVH trees) per
        # pixel, which otherwise dominates render time (minutes of overhead).
        pool = multiprocessing.Pool(
            processes=multiprocessing.cpu_count(),
            initializer=init_worker,
            initargs=(self.width, self.height, self.camera,
                      self.objects, self.lights))
        try:
            for y in range(self.height):
                if not self.running:
                    break

                args = [(x, y) for x in range(self.width)]
                results = pool.starmap(render_pixel_coord, args)

                for x in range(self.width):
                    self.img_array[y, x] = results[x]
                config.render_stats["processed_pixels"] += self.width

                avg_rays_per_pixel = config.AA_SAMPLES * config.AA_SAMPLES * (1 + len(self.lights))
                config.render_stats["ray_count"] = \
                    config.render_stats["processed_pixels"] * avg_rays_per_pixel

                self.update_signal.emit(self.img_array.copy(), y, y + 1)
                self.progress_signal.emit(config.render_stats["processed_pixels"])
        finally:
            pool.close()
            pool.join()

        config.render_stats["end_time"] = time.time()
        self.finished_signal.emit(self.img_array)
    
    def stop(self):
        self.running = False
