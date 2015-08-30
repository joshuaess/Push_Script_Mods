# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modification allows Shift + Encoder to provide fine adjustment and Shift + double tap to reset parameter value.

import Live 
import _Framework.Task
from TouchEncoderElement import TouchEncoderElement, subject_slot

class ShiftableTouchEncoderElement(TouchEncoderElement):
    
    def __init__(self, msg_type, channel, identifier, map_mode, undo_step_handler = None, delete_handler = None, touch_button = None, shift_button = None, *a, **k):
        super(ShiftableTouchEncoderElement, self).__init__(msg_type, channel, identifier, map_mode, undo_step_handler, delete_handler, touch_button, *a, **k)
        self._on_shift_button.subject = shift_button 
        self._tasks = self.canonical_parent._task_group.add(_Framework.Task.TaskGroup()) 
        self._double_tap_task = self._tasks.add(_Framework.Task.sequence(_Framework.Task.delay(2), self._reset_tap_count))
        self._double_tap_task.kill()
        self._tap_count = 0
        
    def disconnect(self):
        self._tasks = None
        self._double_tap_task = None
        super(ShiftableTouchEncoderElement, self).disconnect()
        
    @subject_slot('value')
    def _on_touch_button(self, value): 
        """ Modified to reset param value if encoder double tapped while shift held. """
        self._trigger_undo_step = value
        if value:
            param = self.mapped_parameter()
            if self._on_shift_button.subject and self._on_shift_button.subject.is_pressed():
                self._tap_count += 1
                self._double_tap_task.restart()
                if self._tap_count > 1:
                    if param and not param.is_quantized:
                        param.value = param.default_value
                    self._tap_count = 0    
            if self._delete_handler and self._delete_handler.is_deleting and param:
                self._delete_handler.delete_clip_envelope(param)
            else:
                self.begin_gesture()
                self._observer.on_encoder_touch(self)
                self.notify_touch_value(value)
        else:
            if self._undo_step_handler and self._undo_step_open:
                self._undo_step_handler.end_undo_step()
            self._observer.on_encoder_touch(self)
            self.notify_touch_value(value)
            self.end_gesture()       
            
    def _reset_tap_count(self, args=None): 
        """ Triggered by timer to reset the tap count. """
        self._tap_count = 0        
        
    @subject_slot('value')
    def _on_shift_button(self, value): 
        """ On Shift button pressed, sets fine resolution if possible and resets on release. """
        self._double_tap_task.kill()
        self._tap_count = 0
        if value:
            self._default_sensitivity = self._mapping_sensitivity
            param = self.mapped_parameter()
            if param and isinstance(param, Live.DeviceParameter.DeviceParameter) and param.is_enabled and not param.is_quantized:
                self._mapping_sensitivity = 0.09
        else:
            self._mapping_sensitivity = self._default_sensitivity
    