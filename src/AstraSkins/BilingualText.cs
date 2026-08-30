using System.Globalization;
using System.Text;
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

    public Argument GetArgument(string key)
    {
        var english = Lookup(_en, key, key);
        return new Argument(Lookup(_zh, key, english), english);
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

    public static string Truncate(string value, int maxDisplayWidth)
    {
        if (maxDisplayWidth <= 0 || string.IsNullOrEmpty(value))
        {
            return string.Empty;
        }

        if (DisplayWidth(value) <= maxDisplayWidth)
        {
            return value;
        }

        const string separator = " / ";
        var separatorIndex = value.IndexOf(separator, StringComparison.Ordinal);
        if (separatorIndex > 0 && maxDisplayWidth > separator.Length + 7)
        {
            var contentBudget = maxDisplayWidth - separator.Length;
            var chineseBudget = contentBudget / 2;
            var englishBudget = contentBudget - chineseBudget;
            return TruncateSingle(value[..separatorIndex], chineseBudget) + separator +
                   TruncateSingle(value[(separatorIndex + separator.Length)..], englishBudget);
        }

        return TruncateSingle(value, maxDisplayWidth);
    }

    public static int DisplayWidth(string? value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return 0;
        }

        var width = 0;
        var enumerator = StringInfo.GetTextElementEnumerator(value);
        while (enumerator.MoveNext())
        {
            width += TextElementWidth(enumerator.GetTextElement());
        }

        return width;
    }

    private static string TruncateSingle(string value, int maxDisplayWidth)
    {
        if (DisplayWidth(value) <= maxDisplayWidth)
        {
            return value;
        }

        const string ellipsis = "...";
        var contentBudget = Math.Max(0, maxDisplayWidth - ellipsis.Length);
        if (contentBudget == 0)
        {
            return ellipsis[..Math.Min(maxDisplayWidth, ellipsis.Length)];
        }

        var result = new StringBuilder();
        var used = 0;
        var enumerator = StringInfo.GetTextElementEnumerator(value);
        while (enumerator.MoveNext())
        {
            var element = enumerator.GetTextElement();
            var width = TextElementWidth(element);
            if (used + width > contentBudget)
            {
                break;
            }

            result.Append(element);
            used += width;
        }

        return result.Append(ellipsis).ToString();
    }

    private static int TextElementWidth(string element)
    {
        if (string.IsNullOrEmpty(element))
        {
            return 0;
        }

        var rune = Rune.GetRuneAt(element, 0);
        var value = rune.Value;
        return value >= 0x1100 &&
               (value <= 0x115F ||
                value is 0x2329 or 0x232A ||
                (value >= 0x2E80 && value <= 0xA4CF && value != 0x303F) ||
                (value >= 0xAC00 && value <= 0xD7A3) ||
                (value >= 0xF900 && value <= 0xFAFF) ||
                (value >= 0xFE10 && value <= 0xFE19) ||
                (value >= 0xFE30 && value <= 0xFE6F) ||
                (value >= 0xFF00 && value <= 0xFF60) ||
                (value >= 0xFFE0 && value <= 0xFFE6) ||
                (value >= 0x1F000 && value <= 0x1FAFF) ||
                (value >= 0x20000 && value <= 0x3FFFD))
            ? 2
            : 1;
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
