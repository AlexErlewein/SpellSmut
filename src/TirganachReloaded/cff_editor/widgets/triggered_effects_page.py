from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QTextEdit, QPushButton, QColorDialog, QFormLayout,
    QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QListWidget,
    QListWidgetItem, QPushButton, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


class TriggeredEffectsPage(QWizardPage):
    """Step for configuring triggered effects, auras, and projectiles"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Triggered Effects")
        self.setSubTitle("Configure auras, projectiles, and ongoing effects.")

        layout = QVBoxLayout()

        # Tab widget for different effect types
        self.tab_widget = QTabWidget()
        
        # Aura Effects Tab
        self.tab_widget.addTab(self.create_aura_tab(), "🌟 Aura Effects")
        
        # Projectile System Tab  
        self.tab_widget.addTab(self.create_projectile_tab(), "🏹 Projectile System")
        
        # Triggered Effects Tab
        self.tab_widget.addTab(self.create_triggered_tab(), "⚡ Triggered Effects")
        
        # Sound Effects Tab
        self.tab_widget.addTab(self.create_sound_tab(), "🔊 Sound Effects")
        
        layout.addWidget(self.tab_widget)
        layout.addStretch()
        self.setLayout(layout)

    def create_aura_tab(self):
        """Create aura effects configuration tab"""
        aura_widget = QWidget()
        aura_layout = QVBoxLayout()
        
        # Aura Enable
        aura_group = QGroupBox("Aura Configuration")
        aura_form = QFormLayout()
        
        self.aura_enabled_checkbox = QCheckBox("Enable Aura Effect")
        self.aura_enabled_checkbox.toggled.connect(self.on_aura_toggled)
        aura_form.addRow("Status:", self.aura_enabled_checkbox)
        
        self.aura_radius_spin = QDoubleSpinBox()
        self.aura_radius_spin.setRange(1.0, 50.0)
        self.aura_radius_spin.setValue(5.0)
        self.aura_radius_spin.setSuffix(" meters")
        self.aura_radius_spin.setEnabled(False)
        aura_form.addRow("Aura Radius:", self.aura_radius_spin)
        
        self.aura_duration_spin = QDoubleSpinBox()
        self.aura_duration_spin.setRange(1.0, 300.0)
        self.aura_duration_spin.setValue(10.0)
        self.aura_duration_spin.setSuffix(" seconds")
        self.aura_duration_spin.setEnabled(False)
        aura_form.addRow("Aura Duration:", self.aura_duration_spin)
        
        # Aura Visual Effects
        self.aura_vfx_combo = QComboBox()
        self.aura_vfx_combo.addItems([
            "None",
            "🌟 Holy Glow (golden particles)",
            "🔥 Fire Aura (flame particles)",
            "❄️ Ice Aura (frost crystals)",
            "⚡ Electric Aura (lightning arcs)",
            "🌑 Shadow Aura (dark smoke)",
            "💚 Poison Cloud (green gas)",
            "🛡️ Protection Shield (blue barrier)",
            "✨ Magic Sparkles (colored sparkles)"
        ])
        self.aura_vfx_combo.setEnabled(False)
        aura_form.addRow("Aura Visual:", self.aura_vfx_combo)
        
        aura_group.setLayout(aura_form)
        aura_layout.addWidget(aura_group)
        
        # Aura Effects List
        effects_group = QGroupBox("Aura Effects (comma-separated)")
        effects_layout = QVBoxLayout()
        
        self.aura_effects_edit = QTextEdit()
        self.aura_effects_edit.setPlaceholderText(
            "Examples:\n"
            "heal_5_per_second, damage_3_per_second, slow_30%\n"
            "regeneration_10, armor_boost_5, resistance_fire_25\n"
            "mana_drain_2, fear_aura, invisibility"
        )
        self.aura_effects_edit.setMaximumHeight(80)
        self.aura_effects_edit.setEnabled(False)
        effects_layout.addWidget(self.aura_effects_edit)
        
        effects_group.setLayout(effects_layout)
        aura_layout.addWidget(effects_group)
        
        aura_widget.setLayout(aura_layout)
        return aura_widget

    def create_projectile_tab(self):
        """Create projectile system configuration tab"""
        projectile_widget = QWidget()
        projectile_layout = QVBoxLayout()
        
        # Basic Projectile Settings
        basic_group = QGroupBox("Basic Projectile Settings")
        basic_form = QFormLayout()
        
        self.projectile_count_spin = QSpinBox()
        self.projectile_count_spin.setRange(1, 20)
        self.projectile_count_spin.setValue(1)
        basic_form.addRow("Projectile Count:", self.projectile_count_spin)
        
        self.projectile_speed_spin = QDoubleSpinBox()
        self.projectile_speed_spin.setRange(0.1, 10.0)
        self.projectile_speed_spin.setValue(1.0)
        self.projectile_speed_spin.setSuffix("x speed")
        basic_form.addRow("Projectile Speed:", self.projectile_speed_spin)
        
        self.projectile_spread_spin = QDoubleSpinBox()
        self.projectile_spread_spin.setRange(0.0, 360.0)
        self.projectile_spread_spin.setValue(0.0)
        self.projectile_spread_spin.setSuffix(" degrees")
        basic_form.addRow("Spread Angle:", self.projectile_spread_spin)
        
        self.projectile_gravity_spin = QDoubleSpinBox()
        self.projectile_gravity_spin.setRange(0.0, 5.0)
        self.projectile_gravity_spin.setValue(1.0)
        self.projectile_gravity_spin.setSuffix("x gravity")
        basic_form.addRow("Gravity Effect:", self.projectile_gravity_spin)
        
        basic_group.setLayout(basic_form)
        projectile_layout.addWidget(basic_group)
        
        # Advanced Projectile Properties
        advanced_group = QGroupBox("Advanced Properties")
        advanced_layout = QVBoxLayout()
        
        self.projectile_bounce_checkbox = QCheckBox("Bouncing Projectiles")
        self.projectile_bounce_checkbox.setToolTip("Projectiles bounce off walls and obstacles")
        advanced_layout.addWidget(self.projectile_bounce_checkbox)
        
        self.projectile_pierce_checkbox = QCheckBox("Piercing Projectiles")
        self.projectile_pierce_checkbox.setToolTip("Projectiles pass through multiple enemies")
        advanced_layout.addWidget(self.projectile_pierce_checkbox)
        
        self.projectile_homing_checkbox = QCheckBox("Homing Projectiles")
        self.projectile_homing_checkbox.setToolTip("Projectiles track nearest enemy")
        advanced_layout.addWidget(self.projectile_homing_checkbox)
        
        self.projectile_split_checkbox = QCheckBox("Splitting Projectiles")
        self.projectile_split_checkbox.setToolTip("Projectiles split into smaller ones")
        advanced_layout.addWidget(self.projectile_split_checkbox)
        
        advanced_group.setLayout(advanced_layout)
        projectile_layout.addWidget(advanced_group)
        
        projectile_widget.setLayout(projectile_layout)
        return projectile_widget

    def create_triggered_tab(self):
        """Create triggered effects configuration tab"""
        triggered_widget = QWidget()
        triggered_layout = QVBoxLayout()
        
        # Trigger Conditions
        trigger_group = QGroupBox("Trigger Conditions")
        trigger_form = QFormLayout()
        
        self.trigger_on_hit_checkbox = QCheckBox("On Hit Effect")
        trigger_form.addRow("", self.trigger_on_hit_checkbox)
        
        self.trigger_on_crit_checkbox = QCheckBox("On Critical Hit")
        trigger_form.addRow("", self.trigger_on_crit_checkbox)
        
        self.trigger_on_kill_checkbox = QCheckBox("On Kill Effect")
        trigger_form.addRow("", self.trigger_on_kill_checkbox)
        
        self.trigger_on_timer_checkbox = QCheckBox("Timed Effect")
        trigger_form.addRow("", self.trigger_on_timer_checkbox)
        
        self.trigger_interval_spin = QDoubleSpinBox()
        self.trigger_interval_spin.setRange(0.5, 60.0)
        self.trigger_interval_spin.setValue(3.0)
        self.trigger_interval_spin.setSuffix(" seconds")
        self.trigger_interval_spin.setEnabled(False)
        trigger_form.addRow("Trigger Interval:", self.trigger_interval_spin)
        
        trigger_group.setLayout(trigger_form)
        triggered_layout.addWidget(trigger_group)
        
        # Triggered Effects List
        effects_group = QGroupBox("Triggered Effects")
        effects_layout = QVBoxLayout()
        
        self.triggered_effects_list = QListWidget()
        self.triggered_effects_list.setMaximumHeight(120)
        
        # Add some example effects
        example_effects = [
            "💥 Explosion (area damage)",
            "⛓️ Chain Lightning (jumps to nearby)",
            "🌪 Vortex (pulls enemies)",
            "❄️ Freeze Wave (area slow)",
            "💀 Life Drain (heal caster)",
            "🛡️ Reflect Shield (damage return)",
            "⚡ EMP (disable abilities)",
            "🌑 Shadow Clone (summon duplicate)"
        ]
        
        for effect in example_effects:
            item = QListWidgetItem(effect)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.triggered_effects_list.addItem(item)
        
        effects_layout.addWidget(self.triggered_effects_list)
        
        # Add custom effect button
        custom_layout = QHBoxLayout()
        self.add_custom_effect_btn = QPushButton("Add Custom Effect")
        self.add_custom_effect_btn.clicked.connect(self.add_custom_effect)
        custom_layout.addWidget(self.add_custom_effect_btn)
        custom_layout.addStretch()
        effects_layout.addLayout(custom_layout)
        
        effects_group.setLayout(effects_layout)
        triggered_layout.addWidget(effects_group)
        
        triggered_widget.setLayout(triggered_layout)
        return triggered_widget

    def create_sound_tab(self):
        """Create sound effects configuration tab"""
        sound_widget = QWidget()
        sound_layout = QVBoxLayout()
        
        # Event-based Sounds
        event_group = QGroupBox("Event-Based Sounds")
        event_form = QFormLayout()
        
        self.sound_aura_start_combo = QComboBox()
        self.sound_aura_start_combo.addItems([
            "None",
            "🌟 Holy Chime",
            "🔥 Fire Whoosh",
            "❄️ Ice Crystals",
            "⚡ Electric Hum",
            "🌑 Dark Whisper",
            "💚 Poison Hiss",
            "🛡️ Shield Chime"
        ])
        event_form.addRow("Aura Start:", self.sound_aura_start_combo)
        
        self.sound_aura_loop_combo = QComboBox()
        self.sound_aura_loop_combo.addItems([
            "None",
            "🌟 Holy Ambience",
            "🔥 Fire Crackling",
            "❄️ Ice Wind",
            "⚡ Electric Buzz",
            "🌑 Dark Pulse",
            "💚 Poison Bubbles",
            "🛡️ Shield Hum"
        ])
        event_form.addRow("Aura Loop:", self.sound_aura_loop_combo)
        
        self.sound_projectile_launch_combo = QComboBox()
        self.sound_projectile_launch_combo.addItems([
            "None",
            "🏹 Bow Shot",
            "🔥 Fireball Launch",
            "❄️ Ice Shard",
            "⚡ Lightning Bolt",
            "🌑 Shadow Dart",
            "💚 Poison Spit",
            "✨ Magic Missile"
        ])
        event_form.addRow("Projectile Launch:", self.sound_projectile_launch_combo)
        
        self.sound_trigger_combo = QComboBox()
        self.sound_trigger_combo.addItems([
            "None",
            "💥 Explosion",
            "⛓️ Lightning Crack",
            "🌪 Vortex Roar",
            "❄️ Ice Shatter",
            "💀 Soul Drain",
            "🛡️ Shield Break",
            "⚡ EMP Burst"
        ])
        event_form.addRow("Trigger Effect:", self.sound_trigger_combo)
        
        event_group.setLayout(event_form)
        sound_layout.addWidget(event_group)
        
        sound_widget.setLayout(sound_layout)
        return sound_widget

    def on_aura_toggled(self, checked):
        """Enable/disable aura controls"""
        self.aura_radius_spin.setEnabled(checked)
        self.aura_duration_spin.setEnabled(checked)
        self.aura_vfx_combo.setEnabled(checked)
        self.aura_effects_edit.setEnabled(checked)

    def add_custom_effect(self):
        """Add custom triggered effect"""
        from PySide6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(
            self, "Custom Effect", 
            "Enter custom triggered effect name:"
        )
        if ok and text.strip():
            item = QListWidgetItem(f"✨ {text.strip()}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.triggered_effects_list.addItem(item)

    def get_triggered_effects_data(self):
        """Collect all triggered effects data"""
        data = {}
        
        # Aura data
        data['has_aura'] = self.aura_enabled_checkbox.isChecked()
        data['aura_radius'] = self.aura_radius_spin.value()
        data['aura_duration'] = self.aura_duration_spin.value()
        data['aura_vfx'] = self.aura_vfx_combo.currentText()
        data['aura_effects'] = [e.strip() for e in self.aura_effects_edit.toPlainText().split(',') if e.strip()]
        
        # Projectile data
        data['projectile_count'] = self.projectile_count_spin.value()
        data['projectile_speed'] = self.projectile_speed_spin.value()
        data['projectile_spread'] = self.projectile_spread_spin.value()
        data['projectile_gravity'] = self.projectile_gravity_spin.value()
        data['projectile_bounce'] = self.projectile_bounce_checkbox.isChecked()
        data['projectile_pierce'] = self.projectile_pierce_checkbox.isChecked()
        data['projectile_homing'] = self.projectile_homing_checkbox.isChecked()
        data['projectile_split'] = self.projectile_split_checkbox.isChecked()
        
        # Triggered effects
        checked_effects = []
        for i in range(self.triggered_effects_list.count()):
            item = self.triggered_effects_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_effects.append(item.text())
        data['triggered_effects'] = checked_effects
        
        data['trigger_on_hit'] = self.trigger_on_hit_checkbox.isChecked()
        data['trigger_on_crit'] = self.trigger_on_crit_checkbox.isChecked()
        data['trigger_on_kill'] = self.trigger_on_kill_checkbox.isChecked()
        data['trigger_on_timer'] = self.trigger_on_timer_checkbox.isChecked()
        data['trigger_interval'] = self.trigger_interval_spin.value()
        
        # Sound effects
        data['sound_aura_start'] = self.sound_aura_start_combo.currentText()
        data['sound_aura_loop'] = self.sound_aura_loop_combo.currentText()
        data['sound_projectile_launch'] = self.sound_projectile_launch_combo.currentText()
        data['sound_trigger'] = self.sound_trigger_combo.currentText()
        
        return data

    def isComplete(self) -> bool:
        """Validate page"""
        # Always complete - triggered effects are optional
        return True

    def initializePage(self):
        """Initialize page when shown"""
        self.completeChanged.emit()