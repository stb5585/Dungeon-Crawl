"""Regression coverage for progression-screen selection behavior."""

from types import SimpleNamespace

import pygame
import pytest

from src.core.progression import (
    ABILITY_TREES,
    AbilityTreeNode,
    NodeKind,
    NodeState,
    NodeStatus,
    PurchaseResult,
)
from src.ui_pygame.gui import progression_screen


def _node():
    return AbilityTreeNode(
        id="warrior.ability.test",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Arms",
        position=(0, 1),
        icon_key="skill_offense",
        payload={"name": "Test Talent"},
    )


def test_draw_all_accepts_player_from_shared_popup_contract():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    player = object()
    screen.width = 1024
    screen.height = 768
    screen.colors = SimpleNamespace(GRAY=(128, 128, 128))
    screen.screen = SimpleNamespace(blit=lambda *_args: None)
    screen.small_font = SimpleNamespace(render=lambda *_args: object())
    screen.draw_background = lambda: None
    screen._draw_header = lambda: None
    screen._draw_tree = lambda _rect: None
    screen._draw_attributes = lambda _rect: None
    screen._draw_details = lambda _rect: None

    screen.draw_all(player, do_flip=False)

    assert screen.player_char is player


def test_blocked_node_selection_does_not_stage_or_open_popup(monkeypatch):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen._selected_status = lambda: NodeStatus(
        _node(),
        NodeState.BLOCKED,
        ("Requires Piercing Strike.",),
    )
    monkeypatch.setattr(
        progression_screen,
        "ConfirmationPopup",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("blocked nodes must not open popups")
        ),
    )

    screen._toggle_selected_node()

    assert screen.pending_node_ids == []


def test_available_node_toggles_in_and_out_of_staged_plan():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen._selected_status = lambda: NodeStatus(_node(), NodeState.AVAILABLE)

    screen._toggle_selected_node()
    assert screen.pending_node_ids == ["warrior.ability.test"]

    screen._selected_status = lambda: NodeStatus(_node(), NodeState.OWNED)
    screen._toggle_selected_node()
    assert screen.pending_node_ids == []


def test_paladin_promotion_uses_descriptive_vow_popup_and_confirmation(
    monkeypatch,
):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.presenter = object()
    screen._popup_background = lambda: None
    calls = []

    class FakeVowPopup:
        def __init__(self, presenter):
            calls.append(("vow-init", presenter))

        def show(self, **kwargs):
            calls.append(("vow-show", kwargs))
            return "Protection"

    class FakeConfirmation:
        def __init__(self, presenter, message, show_buttons=False):
            calls.append(("confirm-init", presenter, message, show_buttons))

        def show(self, **kwargs):
            calls.append(("confirm-show", kwargs))
            return True

    monkeypatch.setattr(
        progression_screen,
        "PaladinVowSelectionPopup",
        FakeVowPopup,
    )
    monkeypatch.setattr(
        progression_screen,
        "ConfirmationPopup",
        FakeConfirmation,
    )

    assert screen._promotion_choices("Paladin") == {"vow": "Protection"}
    assert calls[1][1]["background_draw_func"] == screen._popup_background
    assert calls[2][2] == "Swear the Vow of Protection?"
    assert calls[2][3]
    assert calls[3][1]["background_draw_func"] == screen._popup_background


def test_canceling_paladin_vow_confirmation_cancels_promotion_choice(
    monkeypatch,
):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.presenter = object()
    screen._popup_background = lambda: None

    class FakeVowPopup:
        def __init__(self, _presenter):
            pass

        def show(self, **_kwargs):
            return "Redemption"

    class FakeConfirmation:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return False

    monkeypatch.setattr(
        progression_screen,
        "PaladinVowSelectionPopup",
        FakeVowPopup,
    )
    monkeypatch.setattr(
        progression_screen,
        "ConfirmationPopup",
        FakeConfirmation,
    )

    assert screen._promotion_choices("Paladin") is None


def test_spend_button_commits_entire_distribution_once(monkeypatch):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.player_char = SimpleNamespace(
        progression=SimpleNamespace(unspent_points=3),
    )
    screen.pending_node_ids = ["warrior.ability.piercingstrike"]
    screen.pending_attributes = {"strength": 2}
    screen.presenter = object()
    redraws = []
    screen.background_draw_func = lambda: redraws.append(True)
    calls = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            calls.append(("popup", message, show_buttons))

        def show(self, **_kwargs):
            return None

    monkeypatch.setattr(progression_screen, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(
        progression_screen,
        "apply_progression_plan",
        lambda player, node_ids, attributes, **_kwargs: (
            calls.append((player, list(node_ids), dict(attributes)))
            or PurchaseResult(True, "Spent 3 points.")
        ),
    )

    screen._spend_pending()

    assert calls[0][1:] == (
        ["warrior.ability.piercingstrike"],
        {"strength": 2},
    )
    assert len(calls) == 1
    assert redraws == [True]
    assert screen.pending_node_ids == []
    assert screen.pending_attributes == {}


def test_spend_distribution_confirms_permanent_node_closures(monkeypatch):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.player_char = SimpleNamespace(
        cls=SimpleNamespace(name="Mage"),
        progression=SimpleNamespace(unspent_points=5),
    )
    screen.pending_node_ids = ["mage.ability.arcane-tradition"]
    screen.pending_attributes = {}
    screen.presenter = object()
    screen._popup_background = lambda: None
    screen._selected_tree_id = lambda: "Mage"
    popup_messages = []
    applied = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            popup_messages.append((message, show_buttons))

        def show(self, **_kwargs):
            return False

    monkeypatch.setattr(progression_screen, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(
        progression_screen,
        "permanent_closures_for_plan",
        lambda *_args, **_kwargs: ("Classical Force",),
    )
    monkeypatch.setattr(
        progression_screen,
        "apply_progression_plan",
        lambda *_args, **_kwargs: applied.append(True),
    )

    screen._spend_pending()

    assert "Classical Force" in popup_messages[0][0]
    assert popup_messages[0][1] is True
    assert applied == []


def test_attribute_incrementer_adds_and_subtracts_without_mutating_player():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.player_char = SimpleNamespace(
        progression=SimpleNamespace(
            unspent_points=2,
            unspent_attribute_points=2,
        ),
        stats=SimpleNamespace(strength=10),
    )
    screen.current_attribute = 0
    screen._revalidate_pending_nodes = lambda: None

    screen._adjust_selected_attribute(1)
    screen._adjust_selected_attribute(1)
    screen._adjust_selected_attribute(1)

    assert screen.pending_attributes == {"strength": 2}
    assert screen.player_char.stats.strength == 10
    screen._adjust_selected_attribute(-1)
    assert screen.pending_attributes == {"strength": 1}


def test_exit_confirmation_discards_staged_distribution(monkeypatch):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.player_char = SimpleNamespace(
        progression=SimpleNamespace(
            unspent_points=2,
            unspent_attribute_points=2,
        ),
    )
    screen.pending_node_ids = ["warrior.ability.piercingstrike"]
    screen.pending_attributes = {"strength": 1}
    screen.presenter = object()
    screen.background_draw_func = None
    messages = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            messages.append((message, show_buttons))

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr(progression_screen, "ConfirmationPopup", FakePopup)

    assert screen.confirm_discard_pending()
    assert "Distributed points will not be spent" in messages[0][0]
    assert screen.pending_node_ids == []
    assert screen.pending_attributes == {}


def test_reset_clears_distributed_points_without_spending():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.pending_node_ids = ["warrior.ability.piercingstrike"]
    screen.pending_attributes = {"strength": 2}

    screen._reset_pending()

    assert screen.pending_node_ids == []
    assert screen.pending_attributes == {}


def test_spending_a_promotion_reuses_church_promotion_screen(monkeypatch):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.player_char = SimpleNamespace(
        progression=SimpleNamespace(
            unspent_points=2,
            unspent_attribute_points=2,
        ),
    )
    screen.pending_node_ids = ["warrior.promotion.weapon-master"]
    screen.pending_attributes = {}
    screen.presenter = object()
    screen.background_draw_func = None
    screen._promotion_choices = lambda _target: {}
    popup_messages = []
    promotion_screens = []
    committed = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            popup_messages.append((message, show_buttons))

        def show(self, **_kwargs):
            return None

    class FakePromotionScreen:
        def __init__(
            self,
            presenter,
            player_char,
            options,
            option_map,
            current_class,
            pro_level,
        ):
            promotion_screens.append(
                (
                    presenter,
                    player_char,
                    options,
                    option_map,
                    current_class,
                    pro_level,
                )
            )

        def navigate(self):
            return "Weapon Master"

    monkeypatch.setattr(progression_screen, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(progression_screen, "PromotionScreen", FakePromotionScreen)
    monkeypatch.setattr(
        progression_screen,
        "apply_progression_plan",
        lambda *_args, **_kwargs: (
            committed.append(True)
            or PurchaseResult(True, "Spent 2 points.")
        ),
    )

    screen._spend_pending()

    assert committed == [True]
    assert len(promotion_screens) == 1
    assert promotion_screens[0][2] == ["Weapon Master"]
    assert list(promotion_screens[0][3]) == ["Weapon Master"]
    assert promotion_screens[0][4:] == ("Warrior", 1)
    assert popup_messages == []


def test_talent_layout_uses_explicit_columns_and_flows_down():
    arms_root = AbilityTreeNode(
        id="warrior.arms.root",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Arms",
        position=(0, 0),
        icon_key="skill_offense",
        payload={"name": "Arms Root"},
    )
    bulwark_root = AbilityTreeNode(
        id="warrior.bulwark.root",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Bulwark",
        position=(1, 0),
        icon_key="skill_defense",
        payload={"name": "Bulwark Root"},
    )
    arms = AbilityTreeNode(
        id="warrior.arms",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Arms",
        position=(0, 1),
        icon_key="skill_offense",
        prerequisites=(arms_root.id,),
        payload={"name": "Arms"},
    )
    bulwark = AbilityTreeNode(
        id="warrior.bulwark",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Bulwark",
        position=(1, 1),
        icon_key="skill_defense",
        prerequisites=(bulwark_root.id,),
        payload={"name": "Bulwark"},
    )
    arms_promotion = AbilityTreeNode(
        id="warrior.promote.arms",
        tree_id="Warrior",
        kind=NodeKind.PROMOTION,
        lane="Arms",
        position=(0, 2),
        icon_key="promotion",
        prerequisites=(arms.id,),
        payload={"name": "Arms Promotion"},
    )
    bulwark_promotion = AbilityTreeNode(
        id="warrior.promote.bulwark",
        tree_id="Warrior",
        kind=NodeKind.PROMOTION,
        lane="Bulwark",
        position=(1, 2),
        icon_key="promotion",
        prerequisites=(bulwark.id,),
        payload={"name": "Bulwark Promotion"},
    )
    statuses = [
        NodeStatus(node, NodeState.AVAILABLE)
        for node in (
            arms_root,
            bulwark_root,
            arms,
            bulwark,
            arms_promotion,
            bulwark_promotion,
        )
    ]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    panel = pygame.Rect(20, 100, 700, 380)
    screen.current_node = 0
    screen.tree_scroll_row = 0

    rects = screen._layout_node_rects(
        panel,
        statuses,
        ("Arms", "Bulwark"),
    )

    assert rects[0].top == rects[1].top
    assert rects[0].centerx != rects[1].centerx
    assert rects[2].top > rects[0].bottom
    assert rects[3].top > rects[1].bottom
    assert rects[4].top == rects[5].top
    assert rects[4].top > max(rects[2].bottom, rects[3].bottom)


def test_terminal_weapon_tree_explicit_columns_fit_inside_panel():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    panel = pygame.Rect(20, 100, 700, 600)

    for class_name in ("Berserker", "Grandmaster of Arms"):
        tree = ABILITY_TREES[class_name]
        statuses = [
            NodeStatus(node, NodeState.AVAILABLE)
            for node in tree.nodes
        ]
        screen.current_node = 0
        screen.tree_scroll_row = 0

        rects = screen._layout_node_rects(panel, statuses, tree.branches)

        assert all(panel.left <= rect.left for rect in rects)
        assert all(rect.right <= panel.right for rect in rects)


def test_eight_row_dragoon_tree_fits_standard_panel_without_scrolling():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    tree = ABILITY_TREES["Dragoon"]
    statuses = [
        NodeStatus(node, NodeState.AVAILABLE)
        for node in tree.nodes
    ]
    panel = pygame.Rect(24, 100, 716, 525)
    screen.current_node = 0
    screen.tree_scroll_row = 0

    rects = screen._layout_node_rects(panel, statuses, tree.branches)

    assert screen.tree_scroll_row == 0
    assert all(rect.bottom <= screen._tree_viewport.bottom for rect in rects)


def test_eight_row_paladin_tree_fits_standard_panel_without_scrolling():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    tree = ABILITY_TREES["Paladin"]
    statuses = [
        NodeStatus(node, NodeState.AVAILABLE)
        for node in tree.nodes
    ]
    panel = pygame.Rect(24, 100, 716, 525)
    screen.current_node = 0
    screen.tree_scroll_row = 0

    rects = screen._layout_node_rects(panel, statuses, tree.branches)

    assert screen.tree_scroll_row == 0
    assert all(rect.bottom <= screen._tree_viewport.bottom for rect in rects)


@pytest.mark.parametrize(
    "class_name",
    ("Mage", "Sorcerer", "Wizard", "Conjurer", "Thaumaturgist"),
)
def test_mage_line_trees_fit_standard_panel_without_overlap_or_scrolling(
    class_name,
):
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    tree = ABILITY_TREES[class_name]
    statuses = [
        NodeStatus(node, NodeState.AVAILABLE)
        for node in tree.nodes
    ]
    panel = pygame.Rect(24, 100, 716, 525)
    screen.current_node = 0
    screen.tree_scroll_row = 0

    rects = screen._layout_node_rects(panel, statuses, tree.branches)

    assert screen.tree_scroll_row == 0
    assert all(rect.bottom <= screen._tree_viewport.bottom for rect in rects)
    assert all(
        not left.colliderect(right)
        for index, left in enumerate(rects)
        for right in rects[index + 1:]
    )


def test_cross_column_connectors_enter_the_side_of_target_nodes(monkeypatch):
    source = _node()
    target = AbilityTreeNode(
        id="warrior.ability.cross-target",
        tree_id="Warrior",
        kind=NodeKind.ABILITY,
        lane="Vanguard",
        position=(1, 3),
        icon_key="skill_offense",
        prerequisites=(source.id,),
        payload={"name": "Cross Target"},
    )
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    source_rect = pygame.Rect(50, 60, 32, 32)
    target_rect = pygame.Rect(150, 180, 32, 32)
    screen.node_icon_rects = [source_rect, target_rect]
    screen._tree_viewport = pygame.Rect(0, 0, 400, 400)
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: (
            line_points.append(points)
        ),
    )

    screen._draw_connectors([
        NodeStatus(source, NodeState.AVAILABLE),
        NodeStatus(target, NodeState.BLOCKED),
    ])

    assert line_points
    assert line_points[0][-1] == target_rect.midleft


def test_authored_cross_connector_uses_manifest_channel(monkeypatch):
    source = progression_screen.TREE_NODES[
        "warrior.ability.shieldblock"
    ]
    target = progression_screen.TREE_NODES["warrior.ability.retaliate"]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    screen.node_icon_rects = [
        pygame.Rect(450, 160, 32, 32),
        pygame.Rect(238, 390, 32, 32),
    ]
    screen._tree_viewport = pygame.Rect(0, 0, 800, 600)
    screen._tree_column_origin = 114
    screen._tree_lane_width = 141
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: (
            line_points.append(points)
        ),
    )

    screen._draw_connectors([
        NodeStatus(source, NodeState.AVAILABLE),
        NodeStatus(target, NodeState.BLOCKED),
    ])

    expected_channel_x = int(114 + 1.5 * 141)
    assert line_points[0][1][0] == expected_channel_x
    assert line_points[0][2][0] == expected_channel_x


def test_familiar_bond_connector_joins_both_node_side_midpoints(monkeypatch):
    source = progression_screen.TREE_NODES["warlock.ability.familiar-bond"]
    target = progression_screen.TREE_NODES["warlock.ability.familiar-bond-2"]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    source_rect = pygame.Rect(600, 100, 32, 32)
    target_rect = pygame.Rect(600, 400, 32, 32)
    screen.node_icon_rects = [source_rect, target_rect]
    screen._tree_viewport = pygame.Rect(0, 0, 800, 600)
    screen._tree_column_origin = 40
    screen._tree_lane_width = 110
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: line_points.append(points),
    )

    screen._draw_connectors([
        NodeStatus(source, NodeState.AVAILABLE),
        NodeStatus(target, NodeState.BLOCKED),
    ])

    expected_channel_x = int(40 + 5.5 * 110)
    assert line_points == [
        (
            source_rect.midright,
            (expected_channel_x, source_rect.centery),
            (expected_channel_x, target_rect.centery),
            target_rect.midright,
        ),
    ]


@pytest.mark.parametrize(
    ("source_id", "target_id", "channel_column"),
    (
        (
            "mage.ability.fire-inside",
            "mage.ability.classical-force",
            0.5,
        ),
        (
            "mage.ability.mana-rupture",
            "mage.ability.arcane-tradition",
            1.5,
        ),
    ),
)
def test_mage_specialization_connectors_use_midpoint_and_enter_from_top(
    monkeypatch,
    source_id,
    target_id,
    channel_column,
):
    source = progression_screen.TREE_NODES[source_id]
    target = progression_screen.TREE_NODES[target_id]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    source_rect = pygame.Rect(300, 100, 32, 32)
    target_rect = pygame.Rect(
        int(100 + channel_column * 120) - 16,
        360,
        32,
        32,
    )
    screen.node_icon_rects = [source_rect, target_rect]
    screen._tree_viewport = pygame.Rect(0, 0, 800, 600)
    screen._tree_column_origin = 100
    screen._tree_lane_width = 120
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: (
            line_points.append(points)
        ),
    )

    screen._draw_connectors([
        NodeStatus(source, NodeState.AVAILABLE),
        NodeStatus(target, NodeState.BLOCKED),
    ])

    expected_channel_x = int(100 + channel_column * 120)
    assert line_points[0][1][0] == expected_channel_x
    assert line_points[0][2][0] == expected_channel_x
    assert line_points[0][-1] == target_rect.midtop


def test_paladin_oath_connectors_drop_to_promotion_row_before_joining(
    monkeypatch,
):
    judgment = progression_screen.TREE_NODES[
        "paladin.ability.oath-judgment"
    ]
    shelter = progression_screen.TREE_NODES[
        "paladin.ability.oath-shelter"
    ]
    promotion = progression_screen.TREE_NODES[
        "paladin.promotion.crusader"
    ]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    judgment_rect = pygame.Rect(180, 120, 32, 32)
    shelter_rect = pygame.Rect(520, 120, 32, 32)
    promotion_rect = pygame.Rect(350, 500, 32, 32)
    screen.node_icon_rects = [
        judgment_rect,
        shelter_rect,
        promotion_rect,
    ]
    screen._tree_viewport = pygame.Rect(0, 0, 800, 600)
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: (
            line_points.append(points)
        ),
    )

    screen._draw_connectors([
        NodeStatus(judgment, NodeState.AVAILABLE),
        NodeStatus(shelter, NodeState.AVAILABLE),
        NodeStatus(promotion, NodeState.BLOCKED),
    ])

    assert line_points == [
        (
            judgment_rect.midbottom,
            (judgment_rect.centerx, promotion_rect.centery),
            promotion_rect.midleft,
        ),
        (
            shelter_rect.midbottom,
            (shelter_rect.centerx, promotion_rect.centery),
            promotion_rect.midright,
        ),
    ]


def test_lancer_promotion_connectors_stay_in_their_source_columns(monkeypatch):
    vigilant = progression_screen.TREE_NODES[
        "lancer.ability.vigilant-landing"
    ]
    excellence = progression_screen.TREE_NODES[
        "lancer.ability.polearm-excellence"
    ]
    promotion = progression_screen.TREE_NODES["lancer.promotion.dragoon"]
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = object()
    vigilant_rect = pygame.Rect(184, 220, 32, 32)
    excellence_rect = pygame.Rect(544, 390, 32, 32)
    promotion_rect = pygame.Rect(424, 500, 32, 32)
    screen.node_icon_rects = [
        vigilant_rect,
        excellence_rect,
        promotion_rect,
    ]
    screen._tree_viewport = pygame.Rect(0, 0, 800, 600)
    screen._tree_column_origin = 80
    screen._tree_lane_width = 120
    line_points = []
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "lines",
        lambda _screen, _color, _closed, points, _width: (
            line_points.append(points)
        ),
    )

    screen._draw_connectors([
        NodeStatus(vigilant, NodeState.AVAILABLE),
        NodeStatus(excellence, NodeState.AVAILABLE),
        NodeStatus(promotion, NodeState.BLOCKED),
    ])

    assert line_points == [
        (
            vigilant_rect.midright,
            (200, vigilant_rect.centery),
            (200, promotion_rect.top),
            promotion_rect.midtop,
        ),
        (
            excellence_rect.midleft,
            (560, excellence_rect.centery),
            (560, promotion_rect.top),
            promotion_rect.midtop,
        ),
    ]


def test_node_highlight_uses_exact_node_frame_bounds():
    icon_rect = pygame.Rect(50, 60, 32, 32)

    frame_rect = progression_screen.ProgressionScreen._node_frame_rect(
        icon_rect
    )

    assert frame_rect == pygame.Rect(48, 58, 36, 36)


def test_embedded_layout_fills_left_height_and_stacks_right_panels():
    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    captured = {}
    screen._draw_tree = lambda rect: captured.setdefault("tree", rect.copy())
    screen._draw_attributes = lambda rect: captured.setdefault(
        "attributes",
        rect.copy(),
    )
    screen._draw_details = lambda rect: captured.setdefault(
        "details",
        rect.copy(),
    )
    screen._draw_spend_button = lambda rect: captured.setdefault(
        "spend",
        rect.copy(),
    )
    player = SimpleNamespace()
    content = pygame.Rect(18, 80, 1004, 586)

    screen.draw_embedded(player, content)

    assert captured["tree"].top == content.top
    assert captured["tree"].bottom == content.bottom
    assert captured["attributes"].top == content.top
    assert captured["attributes"].height == 320
    assert captured["details"].left == captured["attributes"].left
    assert captured["details"].top == captured["attributes"].bottom + 10
    assert captured["details"].bottom < captured["spend"].top
    assert captured["spend"].bottom == content.bottom


def test_attribute_highlight_previews_increased_value_without_training_text(
    monkeypatch,
):
    class FakeFont:
        def render(self, text, _antialias, _color):
            return text

        def get_height(self):
            return 14

    class FakeScreen:
        def __init__(self):
            self.surfaces = []

        def blit(self, surface, _position):
            self.surfaces.append(surface)

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = FakeScreen()
    screen.normal_font = FakeFont()
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(
        BORDER_COLOR=(1, 1, 1),
        GOLD=(2, 2, 2),
        WHITE=(3, 3, 3),
        HIGHLIGHT_BG=(4, 4, 4),
        GRAY=(5, 5, 5),
    )
    screen.focus = "attributes"
    screen.current_attribute = 2
    screen.pending_attributes = {"wisdom": 1}
    screen.pending_node_ids = []
    screen.player_char = SimpleNamespace(
        progression=SimpleNamespace(
            unspent_points=2,
            unspent_attribute_points=2,
        ),
        stats=SimpleNamespace(
            strength=10,
            intel=10,
            wisdom=10,
            con=10,
            charisma=10,
            dex=10,
        ),
    )
    screen.draw_semi_transparent_panel = lambda *_args, **_kwargs: None
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )

    screen._draw_attributes(pygame.Rect(10, 20, 240, 320))

    assert "Strength: 10 (+0)" in screen.screen.surfaces
    assert "Wisdom: 11 (+1)" in screen.screen.surfaces
    assert "Constitution: 10 (+0)" in screen.screen.surfaces
    assert "Dexterity: 10 (+0)" in screen.screen.surfaces
    assert "Available Attribute Points: 1" in screen.screen.surfaces
    assert all("trained" not in text for text in screen.screen.surfaces)


def test_details_rendering_never_spills_below_panel(monkeypatch):
    class FakeFont:
        def get_height(self):
            return 18

        def size(self, text):
            return (len(text) * 7, 18)

        def render(self, text, _antialias, _color):
            return text

    class FakeScreen:
        def __init__(self):
            self.positions = []
            self.surfaces = []

        def blit(self, surface, position):
            self.surfaces.append(surface)
            self.positions.append(position)

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = FakeScreen()
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(
        BORDER_COLOR=(1, 1, 1),
        GOLD=(2, 2, 2),
        WHITE=(3, 3, 3),
    )
    screen.draw_semi_transparent_panel = lambda *_args, **_kwargs: None
    status = NodeStatus(
        progression_screen.TREE_NODES["warrior.ability.weaponfocus"],
        NodeState.BLOCKED,
        (
            "Requires Charge.",
            "Requires global level 10 (current 1).",
            *(f"Blocker {index}" for index in range(12)),
        ),
    )
    screen._selected_status = lambda: status
    panel = pygame.Rect(10, 20, 500, 120)
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )

    screen._draw_details(panel)

    assert screen.screen.positions
    assert all(
        y + screen.small_font.get_height() <= panel.bottom
        for _x, y in screen.screen.positions
    )
    rendered_text = [
        surface
        for surface in screen.screen.surfaces
        if isinstance(surface, str)
    ]
    assert rendered_text == screen.screen.surfaces
    assert "1 Point" in rendered_text
    assert all("BLOCKED" not in line for line in rendered_text)
    assert all("Lane:" not in line for line in rendered_text)
    assert all("Requires Charge" not in line for line in rendered_text)
    assert "Required level: 10" in rendered_text
    assert all("global level" not in line.lower() for line in rendered_text)


def test_weapon_specialization_requirement_wraps_once_inside_details(monkeypatch):
    class FakeFont:
        def get_height(self):
            return 18

        def size(self, text):
            return (len(text) * 7, 18)

        def render(self, text, _antialias, _color):
            return text

    class FakeScreen:
        def __init__(self):
            self.surfaces = []

        def blit(self, surface, _position):
            self.surfaces.append(surface)

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = FakeScreen()
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(
        BORDER_COLOR=(1, 1, 1),
        GOLD=(2, 2, 2),
        WHITE=(3, 3, 3),
    )
    screen.draw_semi_transparent_panel = lambda *_args, **_kwargs: None
    node = progression_screen.TREE_NODES[
        "weapon-master.ability.reavers-mark"
    ]
    screen._selected_status = lambda: NodeStatus(
        node,
        NodeState.BLOCKED,
        (
            "Requires Battle Axe specialization level 1 (current 0).",
        ),
    )
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )
    panel = pygame.Rect(10, 20, 250, 220)

    screen._draw_details(panel)

    rendered_text = [
        surface
        for surface in screen.screen.surfaces
        if isinstance(surface, str)
    ]
    content_width = panel.width - 20
    assert all(
        screen.small_font.size(line)[0] <= content_width
        for line in rendered_text
    )
    assert sum(
        "specialization level" in line
        for line in rendered_text
    ) == 1
    assert all("(current" not in line for line in rendered_text)


def test_promotion_details_wrap_blocker_and_omit_tree_warning(monkeypatch):
    renders = []

    class FakeFont:
        def get_height(self):
            return 18

        def size(self, text):
            return (len(text) * 7, 18)

        def render(self, text, _antialias, color):
            renders.append((text, color))
            return text

    class FakeScreen:
        def __init__(self):
            self.positions = []

        def blit(self, _surface, position):
            self.positions.append(position)

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = FakeScreen()
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(
        BORDER_COLOR=(1, 1, 1),
        GOLD=(2, 2, 2),
        WHITE=(3, 3, 3),
        GRAY=(4, 4, 4),
    )
    screen.draw_semi_transparent_panel = lambda *_args, **_kwargs: None
    node = progression_screen.TREE_NODES[
        "warrior.promotion.weapon-master"
    ]
    screen._selected_status = lambda: NodeStatus(
        node,
        NodeState.BLOCKED,
        (
            "Requires 2 points.",
            "Requires level 30.",
            "Requires Strength 15 (current 12).",
            "Requires Dex 12 (current 11).",
            "Requires Intelligence 11 (current 10).",
            "Another promotion is already distributed.",
        ),
    )
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )

    panel = pygame.Rect(10, 20, 250, 220)
    screen._draw_details(panel)

    text = "\n".join(line for line, _color in renders)
    unwrapped_text = text.replace("\n", " ")
    assert "Required level: 30" in text
    assert "Required Stats:" in unwrapped_text
    assert "Strength 15" in unwrapped_text
    assert "Dexterity 12" in unwrapped_text
    assert "Intelligence 11" in unwrapped_text
    assert "global" not in text.lower()
    assert "(current" not in text
    assert "Requires 2 points." not in text
    assert "Requires level 30." not in text
    assert "Requires Strength" not in text
    assert "Requires Dex" not in text
    assert "Requires Intelligence" not in text
    assert "Permanent choice:" not in text
    warning_renders = [
        (line, color)
        for line, color in renders
        if line in {"Another promotion is already", "distributed."}
    ]
    assert warning_renders == [
        ("Another promotion is already", screen.PROMOTION_WARNING_COLOR),
        ("distributed.", screen.PROMOTION_WARNING_COLOR),
    ]
    assert all(len(line) * 7 <= panel.width - 28 for line, _color in renders)


def test_tree_warning_moves_to_footer_and_turns_red_for_pending_promotion(
    monkeypatch,
):
    renders = []

    class FakeFont:
        def get_height(self):
            return 18

        def size(self, text):
            return (len(text) * 7, 18)

        def render(self, text, _antialias, color):
            renders.append((text, color))
            return text

    class FakeScreen:
        def blit(self, _surface, _position):
            return None

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = FakeScreen()
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(GRAY=(4, 4, 4))
    screen.pending_node_ids = ["warrior.promotion.weapon-master"]
    screen.pending_attributes = {}
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )

    panel = pygame.Rect(10, 20, 500, 320)
    screen._draw_tree_warning(panel)

    text = " ".join(line for line, _color in renders)
    assert text == (
        "Permanent choice: Buying promotion nodes may prevent the player "
        "from buying learning certain abilities. Choose carefully."
    )
    assert all(
        color == screen.PROMOTION_WARNING_COLOR
        for _line, color in renders
    )
    assert all(len(line) * 7 <= panel.width - 32 for line, _color in renders)


def test_lancer_tree_warning_explains_dragoon_node_retention(monkeypatch):
    renders = []

    class FakeFont:
        def get_height(self):
            return 18

        def size(self, text):
            return (len(text) * 7, 18)

        def render(self, text, _antialias, color):
            renders.append((text, color))
            return text

    screen = progression_screen.ProgressionScreen.__new__(
        progression_screen.ProgressionScreen
    )
    screen.screen = SimpleNamespace(blit=lambda *_args: None)
    screen.small_font = FakeFont()
    screen.colors = SimpleNamespace(GRAY=(4, 4, 4))
    screen.player_char = SimpleNamespace(
        cls=SimpleNamespace(name="Lancer"),
        progression=SimpleNamespace(completed_trees=set()),
    )
    screen.tree_index = 0
    screen.pending_node_ids = ["lancer.promotion.dragoon"]
    screen.pending_attributes = {}
    monkeypatch.setattr(
        progression_screen.pygame.draw,
        "rect",
        lambda *_args, **_kwargs: None,
    )

    screen._draw_tree_warning(pygame.Rect(10, 20, 500, 320))

    text = " ".join(line for line, _color in renders)
    assert text == (
        "Promoting to Dragoon retains all unpurchased Lancer nodes in the "
        "Dragoon tree."
    )
