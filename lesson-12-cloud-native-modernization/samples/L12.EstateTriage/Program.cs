using L12.EstateTriage;

#region program
var apps = Inventory.Load(Path.Combine(AppContext.BaseDirectory, "estate.csv"));
var triaged = apps.Select(a => (App: a, Decision: Triage.Decide(a))).ToList();

Console.WriteLine($"Triage of {apps.Count} applications (illustrative inventory)");
foreach (var (app, d) in triaged)
    Console.WriteLine(
        $"  {app.Name,-17} {app.Framework,-7} {d.Strategy,-10} {d.Target,-16} {d.Path}");

Console.WriteLine("By strategy (7 Rs):");
foreach (var s in Enum.GetValues<Strategy>())
    Console.WriteLine($"  {s,-10} {triaged.Count(t => t.Decision.Strategy == s),2}");

Console.WriteLine("By target:");
foreach (var g in triaged.GroupBy(t => t.Decision.Target).OrderByDescending(g => g.Count()))
    Console.WriteLine($"  {g.Key,-15} {g.Count(),2}");
#endregion
