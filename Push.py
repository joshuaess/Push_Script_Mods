# v1.1.4 for Live 9.1.4 - Modified by Stray on 7/29/2014
# Modified to import and deal with UserSettings file and
# handle imports/init differently depending on UserSettings.
#
# Options allow for:
# - Shift + Display Encoders to finely adjust parameter values and reset parameter values via Shift + double tap Encoders.
# - Shift + Record to toggle Arrangement Record (should not be used with Ditto/Carbon).
# - Step-sequencer input to be velocity-sensitive so that steps turned on will have the velocity that the corresponding button sent.
# - Using SeaPush color scheme choosen by Ableton forum user triant (https://github.com/mrk/seapush).

from PushOG import Push as PushBase
from PushOG import ViewControlComponent, OptionalElement, MultiElement, ComboElement, TransportComponent, Layer, SETTING_WORKFLOW, consts, ButtonMatrixElement, GLOBAL_MAP_MODE, MIDI_CC_TYPE, MIDI_NOTE_TYPE
from PushOG import DoublePressElement, SpecialPhysicalDisplay, create_button, create_modifier_button, create_note_button, PrioritizedResource, Sysex, PadButtonElement, TouchStripElement, recursive_map
from PushOG import SysexValueControl, PlayheadElement, LoopSelectorComponent
from PushOG import TouchEncoderElement, TouchStripControllerComponent, TouchStripEncoderConnection
from UserSettings import *

if SHIFT_RECORD_ARRANGE:
    from ExtSessionRecordingComponent import ExtSessionRecordingComponent as FixedLengthSessionRecordingComponent
else:
    from PushOG import FixedLengthSessionRecordingComponent

if VELOCITY_SENSITIVE_STEP_SEQ:
    from VeloSensStepSeqComponent import DrumGroupFinderComponent, VeloSensStepSeqComponent as StepSeqComponent
    from VeloSensMelodicComponent import VeloSensMelodicComponent as MelodicComponent
else:
    from StepSeqComponent import DrumGroupFinderComponent, StepSeqComponent
    from MelodicComponent import MelodicComponent

class Push(PushBase):
    """ Modified script for Push. """

    def __init__(self, c_instance):
        super(Push, self).__init__(c_instance)
        self.log_message('Push script loaded - Stray modifications v1.1.4')

    def _init_transport_and_recording(self):
	""" Same as in OG. Needed here so ExtSessionRecordingComponent is used if elected. """
        self._view_control = ViewControlComponent(name='View_Control')
        self._view_control.set_enabled(False)
        self._view_control.layer = Layer(prev_track_button=self._nav_left_button, next_track_button=self._nav_right_button, prev_scene_button=OptionalElement(self._nav_up_button, self._settings[SETTING_WORKFLOW], False), next_scene_button=OptionalElement(self._nav_down_button, self._settings[SETTING_WORKFLOW], False), prev_scene_list_button=OptionalElement(self._nav_up_button, self._settings[SETTING_WORKFLOW], True), next_scene_list_button=OptionalElement(self._nav_down_button, self._settings[SETTING_WORKFLOW], True))
        self._session_recording = FixedLengthSessionRecordingComponent(self._clip_creator, self._view_control, name='Session_Recording', is_root=True)
        new_button = MultiElement(self._new_button, self._foot_pedal_button.double_press)
        record_button = MultiElement(self._record_button, self._foot_pedal_button.single_press)
        self._session_recording.layer = Layer(new_button=OptionalElement(new_button, self._settings[SETTING_WORKFLOW], False), scene_list_new_button=OptionalElement(new_button, self._settings[SETTING_WORKFLOW], True), record_button=record_button, automation_button=self._automation_button, new_scene_button=self._with_shift(self._new_button), re_enable_automation_button=self._with_shift(self._automation_button), delete_automation_button=ComboElement(self._automation_button, [self._delete_button]), length_button=self._fixed_length_button, _uses_foot_pedal=self._foot_pedal_button)
        self._session_recording.length_layer = Layer(display_line=self._display_line4, label_display_line=self._display_line3, blank_display_line2=self._display_line2, blank_display_line1=self._display_line1, select_buttons=self._select_buttons, state_buttons=self._track_state_buttons, _notification=self._notification.use_single_line(1))
        self._session_recording.length_layer.priority = consts.DIALOG_PRIORITY
        self._transport = TransportComponent(name='Transport', play_toggle_model_transform=lambda v: v, is_root=True)
        self._transport.layer = Layer(play_button=self._play_button, stop_button=self._with_shift(self._play_button), tap_tempo_button=self._tap_tempo_button, metronome_button=self._metronome_button)

    def _init_step_sequencer(self):
	""" Same as in OG. Needed here so VeloSensStepSeqComponent is used if elected. """
        self._step_sequencer = StepSeqComponent(self._clip_creator, self._skin, name='Step_Sequencer', grid_resolution=self._grid_resolution, note_editor_settings=self._add_note_editor_setting())
        self._step_sequencer._drum_group._do_select_drum_pad = self._selector.on_select_drum_pad
        self._step_sequencer._drum_group._do_quantize_pitch = self._quantize.quantize_pitch
        self._step_sequencer.set_enabled(False)
        self._step_sequencer.layer = self._create_step_sequencer_layer()
        self._audio_loop = LoopSelectorComponent(follow_detail_clip=True, measure_length=1.0, name='Loop_Selector')
        self._audio_loop.set_enabled(False)
        self._audio_loop.layer = Layer(loop_selector_matrix=self._matrix)

    def _init_instrument(self):
        instrument_basic_layer = Layer(octave_strip=self._with_shift(self._touch_strip_control), scales_toggle_button=self._scale_presets_button, octave_up_button=self._octave_up_button, octave_down_button=self._octave_down_button, scale_up_button=self._with_shift(self._octave_up_button), scale_down_button=self._with_shift(self._octave_down_button))
        self._instrument = MelodicComponent(skin=self._skin, is_enabled=False, clip_creator=self._clip_creator, name='Melodic_Component', grid_resolution=self._grid_resolution, note_editor_settings=self._add_note_editor_setting(), layer=self._create_instrument_layer(), instrument_play_layer=instrument_basic_layer + Layer(matrix=self._matrix, touch_strip=self._touch_strip_control, touch_strip_indication=self._with_firmware_version(1, 16, ComboElement(self._touch_strip_control, modifiers=[self._select_button])), touch_strip_toggle=self._with_firmware_version(1, 16, ComboElement(self._touch_strip_tap, modifiers=[self._select_button])), aftertouch_control=self._aftertouch_control, delete_button=self._delete_button), instrument_sequence_layer=instrument_basic_layer + Layer(note_strip=self._touch_strip_control))
        self._on_note_editor_layout_changed.subject = self._instrument
