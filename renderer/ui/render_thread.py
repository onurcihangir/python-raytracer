import time
import numpy as np
import multiprocessing
from PyQt5.QtCore import QThread, pyqtSignal
import config
from renderer.raytracer import render_pixel_with_aa

class RenderThread(QThread):
    """
    Class that runs the render process in a separate thread.
    """
    update_signal = pyqtSignal(np.ndarray, int, int)
    finished_signal = pyqtSignal(np.ndarray)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, width, height, camera, objects, light):
        super().__init__()
        self.width = width
        self.height = height
        self.camera = camera
        self.objects = objects
        self.light = light
        self.img_array = np.zeros((height, width, 3), dtype=np.uint8)
        self.running = True
    
    def run(self):
        config.render_stats["ray_count"] = 0
        config.render_stats["start_time"] = time.time()
        config.render_stats["end_time"] = 0
        config.render_stats["processed_pixels"] = 0
        config.render_stats["total_pixels"] = self.width * self.height
        
        for y in range(self.height):
            if not self.running:
                break
                
            batch = [(x, y) for x in range(self.width)]
            
            pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
            args = [(x, y, self.width, self.height, self.camera, self.objects, self.light) for x, y in batch]
            results = pool.starmap(render_pixel_with_aa, args)
            pool.close()
            pool.join()
            
            for x in range(self.width):
                self.img_array[y, x] = results[x]
            config.render_stats["processed_pixels"] += len(batch)

            avg_rays_per_pixel = config.AA_SAMPLES * config.AA_SAMPLES * 5
            config.render_stats["ray_count"] = config.render_stats["processed_pixels"] * avg_rays_per_pixel
        
            
            self.update_signal.emit(self.img_array.copy(), y, y+1)
            self.progress_signal.emit(config.render_stats["processed_pixels"])
        
        config.render_stats["end_time"] = time.time()
        self.finished_signal.emit(self.img_array)
    
    def stop(self):
        self.running = False
