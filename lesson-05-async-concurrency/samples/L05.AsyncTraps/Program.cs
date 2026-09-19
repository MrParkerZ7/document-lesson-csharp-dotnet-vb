using L05.AsyncTraps;

// Each trap is reproduced on purpose and contained: the program always exits by itself.

Console.WriteLine("await, lowered by hand");
Console.WriteLine($"  premium {await Lowered.GetPremiumLowered():N2} THB");

Console.WriteLine("sync-over-async (.Result) on a one-thread context");
Console.WriteLine($"  await captures the context -> {Deadlock.BlockOnResult(captureContext: true)}");
Console.WriteLine($"  ConfigureAwait(false)      -> {Deadlock.BlockOnResult(captureContext: false)}");

var (callerSaw, contextGot) = AsyncVoid.Run();
Console.WriteLine("async void throws after its first await");
Console.WriteLine($"  the caller's catch saw     -> {callerSaw}");
Console.WriteLine($"  the context received       -> {contextGot}");

Console.WriteLine("fire-and-forget Task.Run that throws");
Console.WriteLine($"  reported only after a GC   -> {FireAndForget.Run()}");
