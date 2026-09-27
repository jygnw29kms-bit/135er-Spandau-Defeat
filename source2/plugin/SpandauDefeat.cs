using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Admin;
using CounterStrikeSharp.API.Modules.Commands;

namespace SpandauDefeat;

public class SpandauDefeatPlugin : BasePlugin
{
    public override string ModuleName => "135er – Spandau Defeat";
    public override string ModuleVersion => "0.1.0";
    public override string ModuleAuthor => "135ER";
    public override string ModuleDescription => "Source 2 / CS2 server rules for the free 135er – Spandau Defeat mod.";

    private int _alliesTickets = 356;
    private int _axisTickets = 356;
    private string _pointA = "neutral";
    private string _pointB = "neutral";
    private string _pointC = "neutral";

    public override void Load(bool hotReload)
    {
        ReadTicketDefaults();
        Server.PrintToConsole($"[SpandauDefeat] loaded v{ModuleVersion}; tickets {_alliesTickets}:{_axisTickets}");
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
