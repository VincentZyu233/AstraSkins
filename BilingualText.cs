using System.Globalization;
using System.Text.Json;

namespace AstraSkins;

public sealed class BilingualText
{
    private readonly IReadOnlyDictionary<string, string> _zh;
    private readonly IReadOnlyDictionary<string, string> _en;

    public BilingualText(string moduleDirectory)
    {
        _zh = Load(Path.Combine(moduleDirectory, "lang", "zh.json"));
        _en = Load(Path.Combine(moduleDirectory, "lang", "en.json"));
    }

    internal BilingualText(IReadOnlyDictionary<string, string> zh, IReadOnlyDictionary<string, string> en)
    {
        _zh = zh;
        _en = en;
    }

    public string Get(string key, params object?[] arguments)
    {
        var englishTemplate = Lookup(_en, key, key);
        var chineseTemplate = Lookup(_zh, key, englishTemplate);
        var zhArguments = arguments.Select(argument => argument is Argument value ? value.Zh : argument).ToArray();
        var enArguments = arguments.Select(argument => argument is Argument value ? value.En : argument).ToArray();
        return Combine(FormatTemplate(chineseTemplate, zhArguments), FormatTemplate(englishTemplate, enArguments));
    }

    public static Argument Arg(string? displayNameZh, string? displayName)
    {
        var english = displayName?.Trim() ?? string.Empty;
        var chinese = string.IsNullOrWhiteSpace(displayNameZh) ? english : displayNameZh.Trim();
        return new Argument(chinese, english);
    }

    public static string Name(string? displayNameZh, string? displayName)
    {
        var value = Arg(displayNameZh, displayName);
        return Combine(value.Zh?.ToString(), value.En?.ToString());
    }

    public static string Combine(string? chinese, string? english)
    {
        var en = english?.Trim() ?? string.Empty;
        var zh = string.IsNullOrWhiteSpace(chinese) ? en : chinese.Trim();
        if (string.Equals(zh, en, StringComparison.OrdinalIgnoreCase))
        {
            return zh;
        }

        if (zh.Length == 0)
        {
            return en;
        }

        return en.Length == 0 ? zh : $"{zh} / {en}";
    }

    public static string Truncate(string value, int maxTextElements)
    {
        if (maxTextElements <= 0 || string.IsNullOrEmpty(value))
        {
            return string.Empty;
        }

        var elements = StringInfo.ParseCombiningCharacters(value);
        if (elements.Length <= maxTextElements)
        {
            return value;
        }

        const string separator = " / ";
        var separatorIndex = value.IndexOf(separator, StringComparison.Ordinal);
        if (separatorIndex > 0 && maxTextElements > separator.Length + 7)
        {
            var contentBudget = maxTextElements - separator.Length;
            var chineseBudget = contentBudget / 2;
            var englishBudget = contentBudget - chineseBudget;
            return TruncateSingle(value[..separatorIndex], chineseBudget) + separator +
                   TruncateSingle(value[(separatorIndex + separator.Length)..], englishBudget);
        }

        return TruncateSingle(value, maxTextElements);
    }

    private static string TruncateSingle(string value, int maxTextElements)
    {
        var elements = StringInfo.ParseCombiningCharacters(value);
        if (elements.Length <= maxTextElements)
        {
            return value;
        }

        const string ellipsis = "...";
        var keep = Math.Max(0, maxTextElements - ellipsis.Length);
        return keep == 0 ? ellipsis[..Math.Min(maxTextElements, ellipsis.Length)] : value[..elements[keep]] + ellipsis;
    }

    private static IReadOnlyDictionary<string, string> Load(string path)
    {
        if (!File.Exists(path))
        {
            throw new InvalidOperationException($"Missing required bilingual language file: {path}");
        }

        try
        {
            return JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(path))
                   ?? throw new InvalidOperationException($"Bilingual language file is empty: {path}");
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException($"Malformed bilingual language file {path}: {exception.Message}", exception);
        }
    }

    private static string Lookup(IReadOnlyDictionary<string, string> values, string key, string fallback)
    {
        return values.TryGetValue(key, out var value) && !string.IsNullOrWhiteSpace(value) ? value : fallback;
    }

    private static string FormatTemplate(string template, object?[] arguments)
    {
        if (arguments.Length == 0)
        {
            return template;
        }

        try
        {
            return string.Format(CultureInfo.InvariantCulture, template, arguments);
        }
        catch (FormatException)
        {
            return template;
        }
    }

    public readonly record struct Argument(object? Zh, object? En);
}
