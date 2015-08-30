# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modification extends standard MelodicComponent to import VeloSensNoteEditorComponent.

from _Framework.ModesComponent import ModesComponent, LayerMode
from MessageBoxComponent import Messenger
from InstrumentComponent import InstrumentComponent
from PlayheadComponent import PlayheadComponent
from LoopSelectorComponent import LoopSelectorComponent
from NoteEditorPaginator import NoteEditorPaginator
from MelodicComponent import MelodicComponent, NUM_NOTE_EDITORS
from VeloSensNoteEditorComponent import VeloSensNoteEditorComponent as NoteEditorComponent

class VeloSensMelodicComponent(MelodicComponent):

    def __init__(self, clip_creator = None, parameter_provider = None, grid_resolution = None, note_editor_settings = None, skin = None, instrument_play_layer = None, instrument_sequence_layer = None, layer = None, *a, **k):
        super(MelodicComponent, self).__init__(*a, **k)
        self._matrices = None
        self._grid_resolution = grid_resolution
        self._instrument = self.register_component(InstrumentComponent())
        self._note_editors = self.register_components(*[ NoteEditorComponent(settings_mode=note_editor_settings, clip_creator=clip_creator, grid_resolution=self._grid_resolution, is_enabled=False) for _ in xrange(NUM_NOTE_EDITORS) ])
        self._paginator = NoteEditorPaginator(self._note_editors)
        self._loop_selector = self.register_component(LoopSelectorComponent(clip_creator=clip_creator, paginator=self._paginator, is_enabled=False))
        self._playhead = None
        self._playhead_component = self.register_component(PlayheadComponent(grid_resolution=grid_resolution, paginator=self._paginator, follower=self._loop_selector, is_enabled=False))
        self.add_mode('play', LayerMode(self._instrument, instrument_play_layer))
        self.add_mode('sequence', [LayerMode(self._instrument, instrument_sequence_layer),
         self._loop_selector,
         note_editor_settings,
         LayerMode(self, layer),
         self._playhead_component] + self._note_editors)
        self.selected_mode = 'play'
        scales = self._instrument.scales
        self._on_detail_clip_changed.subject = self.song().view
        self._on_scales_changed.subject = scales
        self._on_scales_preset_changed.subject = scales._presets
        self._on_notes_changed.subject = self._instrument
        self._on_selected_mode_changed.subject = self
        self._on_detail_clip_changed()
        self._update_note_editors()
        self._skin = skin
        self._playhead_color = 'Melodic.Playhead'
        self._update_playhead_color()