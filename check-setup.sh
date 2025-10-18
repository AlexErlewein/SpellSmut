#!/bin/bash

echo "======================================"
echo "Environment Setup Verification"
echo "======================================"
echo ""

# Check Crush CLI
if command -v crush &> /dev/null; then
    echo "✅ Crush CLI: $(crush --version 2>&1 | grep version)"
else
    echo "❌ Crush CLI: Not installed"
fi

# Check OpenCode
if command -v opencode.cmd &> /dev/null; then
    echo "✅ OpenCode: $(opencode.cmd --version 2>&1)"
else
    echo "❌ OpenCode: Not installed"
fi

echo ""
echo "Environment Variables:"
echo "----------------------"

# Check API keys
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN: ${GITHUB_TOKEN:0:20}..."
else
    echo "❌ GITHUB_TOKEN: Not set"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}..."
else
    echo "⚠️  ANTHROPIC_API_KEY: Not set"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY: ${OPENAI_API_KEY:0:20}..."
else
    echo "⚠️  OPENAI_API_KEY: Not set"
fi

if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "✅ OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:0:20}..."
else
    echo "⚠️  OPENROUTER_API_KEY: Not set"
fi

if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ GEMINI_API_KEY: ${GEMINI_API_KEY:0:20}..."
else
    echo "⚠️  GEMINI_API_KEY: Not set"
fi

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""

# Count missing keys
missing=0
[ -z "$ANTHROPIC_API_KEY" ] && ((missing++))
[ -z "$OPENAI_API_KEY" ] && ((missing++))
[ -z "$OPENROUTER_API_KEY" ] && ((missing++))
[ -z "$GEMINI_API_KEY" ] && ((missing++))

if [ $missing -eq 4 ]; then
    echo "⚠️  No AI provider API keys configured!"
    echo ""
    echo "To use Crush CLI, run:"
    echo "  ./setup-api-keys.sh"
elif [ $missing -gt 0 ]; then
    echo "✅ You have at least one API key configured!"
    echo ""
    echo "To add more providers, run:"
    echo "  ./setup-api-keys.sh"
else
    echo "🎉 All API keys configured!"
fi

echo ""
echo "To start using Crush CLI:"
echo "  crush"
echo ""
echo "For more info, read:"
echo "  cat CRUSH-QUICKSTART.md"
echo ""

