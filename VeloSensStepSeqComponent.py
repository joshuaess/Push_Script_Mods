# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modification extends standard StepSeqComponent to import VeloSensNoteEditorComponent.

from itertools import imap, chain, starmap
from _Framework.CompoundComponent import CompoundComponent
from DrumGroupComponent import DrumGroupComponent
from GridResolution import GridResolution
from LoopSelectorComponent import LoopSelectorComponent
from PlayheadComponent import PlayheadComponent
from NoteEditorPaginator import NoteEditorPaginator
from StepSeqComponent import StepSeqComponent, DrumGroupFinderComponent
from VeloSensNoteEditorComponent import VeloSensNoteEditorComponent as NoteEditorComponent

class VeloSensStepSeqComponent(StepSeqComponent):
    """ Step Sequencer Component """

    def __init__(self, clip_creator = None, skin = None, grid_resolution = None, note_editor_settings = None, *a, **k):
        super(StepSeqComponent, self).__init__(*a, **k)
        assert clip_creator
        assert skin
        self._grid_resolution = grid_resolution
        note_editor_settings and self.register_component(note_editor_settings)
        self._note_editor, self._loop_selector, self._big_loop_selector, self._drum_group = self.register_components(NoteEditorComponent(settings_mode=note_editor_settings, clip_creator=clip_creator, grid_resolution=self._grid_resolution), LoopSelectorComponent(clip_creator=clip_creator), LoopSelectorComponent(clip_creator=clip_creator, measure_length=2.0), DrumGroupComponent())
        self._paginator = NoteEditorPaginator([self._note_editor])
        self._big_loop_selector.set_enabled(False)
        self._big_loop_selector.set_paginator(self._paginator)
        self._loop_selector.set_paginator(self._paginator)
        self._shift_button = None
        self._delete_button = None
        self._mute_button = None
        self._solo_button = None
        self._note_editor_matrix = None
        self._on_pressed_pads_changed.subject = self._drum_group
        self._on_detail_clip_changed.subject = self.song().view
        self._detail_clip = None
        self._playhead = None
        self._playhead_component = self.register_component(PlayheadComponent(grid_resolution=grid_resolution, paginator=self._paginator, follower=self._loop_selector, notes=chain(*starmap(range, ((92, 100),
         (84, 92),
         (76, 84),
         (68, 76)))), triplet_notes=chain(*starmap(range, ((92, 98),
         (84, 90),
         (76, 82),
         (68, 74))))))
        self._skin = skin
        self._playhead_color = 'NoteEditor.Playhead'