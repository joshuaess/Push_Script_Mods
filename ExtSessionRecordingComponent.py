# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modification extends standard SessionRecordingComponent so that record button will toggle arrange record with shift.

from _Framework.SubjectSlot import subject_slot
from SessionRecordingComponent import FixedLengthSessionRecordingComponent

class ExtSessionRecordingComponent(FixedLengthSessionRecordingComponent):
    
    @subject_slot('value')
    def _on_record_button_value(self, value):
        if self.is_enabled() and value:
            if self.canonical_parent._shift_button.is_pressed():
                self.song().record_mode = not self.song().record_mode
            else:
                if not self._stop_recording():
                    self._start_recording()