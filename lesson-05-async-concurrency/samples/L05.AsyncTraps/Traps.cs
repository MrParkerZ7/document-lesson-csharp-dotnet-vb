using System.Runtime.CompilerServices;

namespace L05.AsyncTraps;

public static class Lowered
{
    #region lowered
    // async Task<decimal> GetPremiumAsync() { await Task.Delay(50); return 8_933.71m; }
    // written out by hand (the real output is a state-machine struct)
    public static Task<decimal> GetPremiumLowered()
    {
        var result = new TaskCompletionSource<decimal>();
        var awaiter = Task.Delay(50).GetAwaiter();
        if (awaiter.IsCompleted) Resume();    // already done: no suspension at all
        else awaiter.OnCompleted(Resume);     // suspend: this thread is free until the timer fires
        return result.Task;                   // the caller gets a Task straight away

        void Resume()                         // everything after the await
        {
            try { awaiter.GetResult(); result.SetResult(8_933.71m); }   // rethrows a failure
            catch (Exception ex) { result.SetException(ex); }
        }
    }
    #endregion
}

public static class Deadlock
{
    #region deadlock
    // library code: awaits with or without ConfigureAwait(false)
    private static async Task<decimal> GetPremiumAsync(bool captureContext)
    {
        await Task.Delay(50).ConfigureAwait(captureContext);
        return 8_933.71m;   // with a captured context, this line must run ON that context's thread
    }

    // a "UI thread": owns a one-thread context, then blocks on .Result
    public static string BlockOnResult(bool captureContext)
    {
        var finished = new ManualResetEventSlim();
        var uiThread = new Thread(() =>
        {
            SynchronizationContext.SetSynchronizationContext(new OneThreadContext());
            _ = GetPremiumAsync(captureContext).Result;   // sync-over-async: this thread now waits
            finished.Set();
        }) { IsBackground = true };
        uiThread.Start();
        // the continuation is queued to uiThread, and uiThread is waiting for the continuation
        return finished.Wait(TimeSpan.FromSeconds(1)) ? "completed" : "DEADLOCK (gave up after 1 s)";
    }
    #endregion
}

public static class AsyncVoid
{
    #region async-void
    private static async void SendQuoteEmail()          // async void: nothing to await
    {
        await Task.Delay(20);
        throw new InvalidOperationException("SMTP relay refused the message");
    }

    public static (string CallerSaw, string ContextGot) Run()
    {
        var context = new OneThreadContext();
        return context.RunOnOwnThread(() =>
        {
            var callerSaw = "nothing";
            try
            {
                SendQuoteEmail();                       // returns at its first await
            }
            catch (Exception ex)
            {
                callerSaw = ex.GetType().Name;          // never reached
            }
            // the exception is re-thrown on the captured context, not to the caller
            var escaped = context.PumpUntilException(TimeSpan.FromSeconds(2));
            return (callerSaw, escaped?.GetType().Name ?? "nothing");
        });
    }
    #endregion
}

public static class FireAndForget
{
    #region fire-and-forget
    public static bool Run()
    {
        var noticed = false;
        TaskScheduler.UnobservedTaskException += (_, e) => { noticed = true; e.SetObserved(); };

        var forgotten = StartAndForget();                    // nobody awaits the task
        SpinWait.SpinUntil(() => !forgotten.TryGetTarget(out var t) || t.IsCompleted);

        GC.Collect();                    // the failure is reported only when the GC finalizes
        GC.WaitForPendingFinalizers();   // the faulted Task — seconds, hours or never later
        return noticed;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static WeakReference<Task> StartAndForget() => new(Task.Run(CallSlowPartner));

    private static void CallSlowPartner() => throw new TimeoutException("P11 did not answer");
    #endregion
}
