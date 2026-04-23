using HAL_IMS_MVC.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();

// HTTP client for FastAPI
builder.Services.AddHttpClient<HalApiService>(client =>
{
    client.BaseAddress = new Uri("http://127.0.0.1:8000/");
    client.Timeout = TimeSpan.FromSeconds(60);
});

var app = builder.Build();

if (!app.Environment.IsDevelopment())
    app.UseExceptionHandler("/Home/Error");

app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Identify}/{action=Index}/{id?}");

app.Run();