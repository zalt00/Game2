# -*- coding:Utf-8 -*-


class CameraMovementTrajectory:
    def __init__(self, base_point, target, total_duration, fade_in, fade_out):
        self.base_point = base_point
        self.target = target
        self.duration = total_duration
        self.fade_in = fade_in
        self.fade_out = fade_out
        
        self.dx = self.target[0] - self.base_point[0]
        self.dy = self.target[1] - self.base_point[1]
        
        self.dtl = self.duration - self.fade_in - self.fade_out
        self.vxl = self.dx / (self.fade_in / 2 + self.dtl + self.fade_out / 2)
        self.vyl = self.dy / (self.fade_in / 2 + self.dtl + self.fade_out / 2)        
        
        if fade_in:
            self.axin = self.vxl / self.fade_in
            self.ayin = self.vyl / self.fade_in
            self.dxin = 0.5 * self.axin * (self.fade_in ** 2)  # distance parcourue à la fin du fade in
            self.dyin = 0.5 * self.ayin * (self.fade_in ** 2)
        else:
            self.dxin = self.dyin = 0
            
        if fade_out:
            self.axout = self.vxl / self.fade_out
            self.ayout = self.vyl / self.fade_out
            self.dxout = 0.5 * self.axout * (self.fade_out ** 2)  # distance parcourue à la fin du fade out
            self.dyout = 0.5 * self.ayout * (self.fade_out ** 2)
        else:  
            self.dxout = self.dyout = 0
            
        self.dxl = self.dx - self.dxin - self.dxout  # distance parcourue en equation lineaire (vt + x0)
        self.dyl = self.dy - self.dyin - self.dyout
        
    def __call__(self, t):
        if t <= self.fade_in:
            x = 0.5 * self.axin * t ** 2 + self.base_point[0]
            y = 0.5 * self.ayin * t ** 2 + self.base_point[1]
        elif self.fade_in < t <= (self.fade_in + self.dtl):
            t2 = t - self.fade_in
            x = self.vxl * t2 + self.base_point[0] + self.dxin
            y = self.vyl * t2 + self.base_point[1] + self.dyin
        elif (self.fade_in + self.dtl) < t <= self.duration:
            t3 = t - self.fade_in - self.dtl
            x = 0.5 * -self.axout * t3 ** 2 + self.vxl * t3 + self.base_point[0] + self.dxin + self.dxl
            y = 0.5 * -self.ayout * t3 ** 2 + self.vyl * t3 + self.base_point[1] + self.dyin + self.dyl
        return x, y
        
