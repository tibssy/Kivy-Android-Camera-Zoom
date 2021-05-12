from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera
from kivy.lang import Builder
import numpy as np
import cv2


Builder.load_file("myapplayout.kv")

class AndroidCamera(Camera):
    camera_resolution = (960, 720)
    displayed_resolution = (640, 480)


    def _camera_loaded(self, *largs):
        self.texture = Texture.create(size=np.flip(self.displayed_resolution), colorfmt='rgb')
        self.texture_size = list(self.texture.size)

    def on_tex(self, *l):
        if self._camera._buffer is None:
            return None
        frame = self.frame_from_buf()

        frame = self.camera_zoom(frame)

        self.frame_to_screen(frame)
        super(AndroidCamera, self).on_tex(*l)

    def frame_from_buf(self):
        w, h = self.resolution
        frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w))
        frame_bgr = cv2.cvtColor(frame, 93)
        return np.rot90(frame_bgr, 3)

    def frame_to_screen(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        flipped = np.flip(frame_rgb, 0)
        buf = flipped.tostring()
        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

    def camera_zoom(self, frame):
        if self.zoom != 1.0:
            x = int((self.camera_resolution[1] - self.camera_resolution[1] / self.zoom) / 2)
            y = int((self.camera_resolution[0] - self.camera_resolution[0] / self.zoom) / 2)
            frame = frame[y:-y, x:-x]
        return cv2.resize(frame, (self.displayed_resolution[1], self.displayed_resolution[0]))


class MyLayout(BoxLayout):

    def zoom_image(self, *args):
        self.ids.acam.zoom = float(args[1])
        self.ids.slider_value.text = f'{round(args[1], 1)}x'

class MyApp(App):
    def build(self):
        return MyLayout()

if __name__ == '__main__':
    MyApp().run()
