# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modification extends standard NoteEditorComponent to store last received velocity and use it when adding steps.

from NoteEditorComponent import NoteEditorComponent, most_significant_note, subject_slot, Subject, create_clip_in_selected_slot

class VeloSensNoteEditorComponent(NoteEditorComponent):
    
    def __init__(self, settings_mode = None, clip_creator = None, grid_resolution = None, *a, **k):
        self._last_velocity = 100
        NoteEditorComponent.__init__(self, settings_mode, clip_creator, grid_resolution, *a, **k)

    @subject_slot('value') 
    def _on_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled():
            if value:
                self._last_velocity = value
            if self._sequencer_clip == None and value or not is_momentary:
                clip = create_clip_in_selected_slot(self._clip_creator, self.song())
                self.set_detail_clip(clip)
            if self._note_index != None:
                width = self._width * self._triplet_factor if self._is_triplet_quantization() else self._width
                if x < width and y < self._height:
                    if value or not is_momentary:
                        self._on_press_step((x, y))
                    else:
                        self._on_release_step((x, y))
                    self._update_editor_matrix()
    
    def _add_note_in_step(self, step, modify_existing = True): 
        """
        Add note in given step if there are none in there, otherwise
        select the step for potential deletion or modification
        """
        if self._sequencer_clip != None:
            x, y = step
            time = self._get_step_start_time(x, y)
            notes = self._time_step(time).filter_notes(self._clip_notes)
            if notes:
                if modify_existing:
                    most_significant_velocity = most_significant_note(notes)[3]
                    if self._mute_button and self._mute_button.is_pressed() or most_significant_velocity != 127 and self.full_velocity:
                        self._trigger_modification(step, immediate=True)
            else:
                pitch = self._note_index
                mute = self._mute_button and self._mute_button.is_pressed()
                velocity = 127 if self.full_velocity else self._last_velocity
                note = (pitch,
                 time,
                 self._get_step_length(),
                 velocity,
                 mute)
                self._sequencer_clip.set_notes((note,))
                self._sequencer_clip.deselect_all_notes()
                self._trigger_modification(step, done=True)
                return True
        return False
    