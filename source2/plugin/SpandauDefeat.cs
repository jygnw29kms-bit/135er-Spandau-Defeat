using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Admin;
using CounterStrikeSharp.API.Modules.Commands;
using CounterStrikeSharp.API.Modules.Timers;

namespace SpandauDefeat;

public class SpandauDefeatPlugin : BasePlugin
{
    public override string ModuleName => "135er – Spandau Defeat";
    public override string ModuleVersion => "0.2.0-source2-alpha";
    public override string ModuleAuthor => "135ER";
    public override string ModuleDescription => "Source 2 / CS2 server rules for the free 135er – Spandau Defeat mod.";

    private int _alliesTickets = 356;
    private int _axisTickets = 356;
    private string _pointA = "neutral";
    private string _pointB = "neutral";
    private string _pointC = "neutral";
    private static readonly string[] MapIds =
    {
        "rathaus_spandau","zitadelle","staaken","rodelberg","kiesteich","falkenhagener_feld",
        "lynarstrasse","wroehmaennerpark","freiheit","fort_hahneberg_1945","teufelsberg_coldwar",
        "flugplatz_gatow_1945","gatow_luftbruecke_1948","radeland_1945",
        "hakenfelde_heeresamt_1944","zitadelle_1945","britischer_sektor_spandau"
    };

    public override void Load(bool hotReload)
    {
        ReadTicketDefaults();
        RegisterEventHandler<EventPlayerDeath>(OnPlayerDeath);
        AddTimer(10.0f, ApplyAutomaticBleed, TimerFlags.REPEAT);
        Server.PrintToConsole($"[SpandauDefeat] loaded v{ModuleVersion}; tickets {_alliesTickets}:{_axisTickets}; maps {MapIds.Length}");
    }

    private HookResult OnPlayerDeath(EventPlayerDeath ev, GameEventInfo info)
    {
        var victim = ev.Userid;
        if (victim != null)
        {
            if (victim.TeamNum == 3) _alliesTickets = Math.Max(0, _alliesTickets - 1);
            else if (victim.TeamNum == 2) _axisTickets = Math.Max(0, _axisTickets - 1);
        }
        return HookResult.Continue;
    }

    private void ApplyAutomaticBleed()
    {
        var alliesOwned = new[] { _pointA, _pointB, _pointC }.Count(x => x == "allies");
        var axisOwned = new[] { _pointA, _pointB, _pointC }.Count(x => x == "axis");
        if (alliesOwned == 3) _axisTickets = Math.Max(0, _axisTickets - 1);
        if (axisOwned == 3) _alliesTickets = Math.Max(0, _alliesTickets - 1);
    }

    private void ReadTicketDefaults()
    {
        var env = Environment.GetEnvironmentVariable("SD_TICKETS");
        if (int.TryParse(env, out var n) && n > 0)
            _alliesTickets = _axisTickets = n;
    }

    private static string NormalizeTeam(string value)
    {
        value = (value ?? "").Trim().ToLowerInvariant();
        return value switch
        {
            "allies" or "ct" or "blue" => "allies",
            "axis" or "t" or "red" => "axis",
            _ => "neutral"
        };
    }

    private void PublishState(CommandInfo info)
    {
        info.ReplyToCommand($"[SpandauDefeat] Tickets Allies {_alliesTickets} | Axis {_axisTickets}");
        info.ReplyToCommand($"[SpandauDefeat] A={_pointA} B={_pointB} C={_pointC}");
    }

    [ConsoleCommand("css_sd_status", "Show Spandau Defeat ticket/objective state")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    public void Status(CCSPlayerController? player, CommandInfo info) => PublishState(info);

    [ConsoleCommand("css_sd_info", "Show build and engine information")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    public void Info(CCSPlayerController? player, CommandInfo info)
    {
        info.ReplyToCommand($"[SpandauDefeat] {ModuleName} {ModuleVersion}");
        info.ReplyToCommand("[SpandauDefeat] Runtime: Counter-Strike 2 / Source 2 · Linux Dedicated Server · CounterStrikeSharp");
        info.ReplyToCommand($"[SpandauDefeat] Maps registered: {MapIds.Length} · Objectives: A/B/C · Free non-commercial mod.");
    }

    [ConsoleCommand("css_sd_maps", "List all registered Spandau Defeat map ids")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    public void Maps(CCSPlayerController? player, CommandInfo info)
    {
        info.ReplyToCommand($"[SpandauDefeat] Maps ({MapIds.Length}): {string.Join(", ", MapIds)}");
    }

    [ConsoleCommand("css_sd_tickets", "Set tickets for both teams")]
    [CommandHelper(minArgs: 1, usage: "<count>", whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    [RequiresPermissions("@css/root")]
    public void Tickets(CCSPlayerController? player, CommandInfo info)
    {
        if (!int.TryParse(info.ArgByIndex(1), out var n) || n < 1 || n > 10000)
        {
            info.ReplyToCommand("[SpandauDefeat] Usage: css_sd_tickets <1..10000>");
            return;
        }
        _alliesTickets = _axisTickets = n;
        PublishState(info);
    }

    [ConsoleCommand("css_sd_point", "Set capture point owner")]
    [CommandHelper(minArgs: 2, usage: "<A|B|C> <allies|axis|neutral>", whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    [RequiresPermissions("@css/root")]
    public void Point(CCSPlayerController? player, CommandInfo info)
    {
        var id = info.ArgByIndex(1).Trim().ToUpperInvariant();
        var owner = NormalizeTeam(info.ArgByIndex(2));
        switch (id)
        {
            case "A": _pointA = owner; break;
            case "B": _pointB = owner; break;
            case "C": _pointC = owner; break;
            default:
                info.ReplyToCommand("[SpandauDefeat] Point must be A, B or C.");
                return;
        }
        PublishState(info);
    }

    [ConsoleCommand("css_sd_bleed", "Apply ticket bleed once based on current objective ownership")]
    [RequiresPermissions("@css/root")]
    public void Bleed(CCSPlayerController? player, CommandInfo info)
    {
        var a = new[] { _pointA, _pointB, _pointC }.Count(x => x == "allies");
        var x = new[] { _pointA, _pointB, _pointC }.Count(v => v == "axis");
        if (a == 3) _axisTickets = Math.Max(0, _axisTickets - 1);
        if (x == 3) _alliesTickets = Math.Max(0, _alliesTickets - 1);
        PublishState(info);
    }

    [ConsoleCommand("css_sd_map", "Load a Spandau map by workshop/map id or compiled map name")]
    [CommandHelper(minArgs: 1, usage: "<map>", whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    [RequiresPermissions("@css/root")]
    public void Map(CCSPlayerController? player, CommandInfo info)
    {
        var map = info.ArgByIndex(1).Trim();
        if (string.IsNullOrWhiteSpace(map) || map.Contains(';') || map.Contains('\n') || map.Contains('\r'))
        {
            info.ReplyToCommand("[SpandauDefeat] Invalid map.");
            return;
        }
        Server.ExecuteCommand($"changelevel {map}");
    }

    [ConsoleCommand("css_sd_bots", "Configure Spandau Defeat bots")]
    [CommandHelper(minArgs: 1, usage: "<0|5|10|15|20> [easy|normal|hard|expert]", whoCanExecute: CommandUsage.CLIENT_AND_SERVER)]
    [RequiresPermissions("@css/root")]
    public void Bots(CCSPlayerController? player, CommandInfo info)
    {
        if (!int.TryParse(info.ArgByIndex(1), out var count) || count is < 0 or > 20)
        {
            info.ReplyToCommand("[SpandauDefeat] Usage: css_sd_bots <0|5|10|15|20> [easy|normal|hard|expert]");
            return;
        }
        var difficulty = info.ArgCount >= 3 ? info.ArgByIndex(2).Trim().ToLowerInvariant() : "normal";
        var level = difficulty switch { "easy" => 0, "normal" => 1, "hard" => 2, "expert" => 3, _ => 1 };
        foreach (var c in new[]
        {
            "bot_kick",
            "bot_join_after_player 0",
            "bot_auto_vacate 1",
            "bot_join_team any",
            "bot_quota_mode fill",
            $"bot_difficulty {level}",
            $"bot_quota {count}"
        }) Server.ExecuteCommand(c);
        info.ReplyToCommand($"[SpandauDefeat] bots={count}, difficulty={difficulty}");
    }

    [ConsoleCommand("css_sd_mode", "Apply Spandau Defeat base CS2 rules")]
    [RequiresPermissions("@css/root")]
    public void Mode(CCSPlayerController? player, CommandInfo info)
    {
        foreach (var c in new[]
        {
            "exec spandau_defeat.cfg",
            "mp_autoteambalance 1",
            "mp_limitteams 1",
            "mp_friendlyfire 0",
            "mp_respawn_on_death_t 1",
            "mp_respawn_on_death_ct 1",
            "mp_restartgame 1"
        }) Server.ExecuteCommand(c);
        info.ReplyToCommand("[SpandauDefeat] mode applied.");
    }
}
