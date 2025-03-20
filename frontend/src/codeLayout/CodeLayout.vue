<template>
    <div class="grid grid-cols-12 h-screen">
        <!-- Left Panel: Markdown Question -->
        <div class="col-span-3 bg-gray-100 dark:bg-gray-800 p-6 overflow-auto border-r">
            <div class="markdown-content">
                <div v-html="compiledMarkdown"></div>
            </div>
        </div>

        <!-- Middle Panel: Python Code Editor -->
        <div class="col-span-6 flex flex-col border rounded-lg overflow-hidden h-full">
            <div class="p-2 bg-gray-200 dark:bg-gray-900 flex justify-between items-center">
                <span class="text-lg font-semibold">Python Code Editor</span>
                <button @click="runCode" class="bg-blue-500 text-white px-4 py-2 rounded-lg">
                    Run Code
                </button>
            </div>
            <div ref="editorContainer" class="flex-1 min-h-0 overflow-hidden"></div>
            <div class="bg-gray-100 dark:bg-gray-800 border-t">
                <div class="p-2">
                    <h2 class="text-md font-semibold mb-2">Output</h2>
                    <pre class="bg-gray-200 dark:bg-gray-900 p-3 rounded-md whitespace-pre-wrap h-32 overflow-y-auto font-mono text-sm">{{ output }}</pre>
                </div>
            </div>
        </div>

        <!-- Right Panel: AI Assistant -->
        <div class="col-span-3 flex flex-col border rounded-lg overflow-hidden">
            <div class="p-2 bg-gray-200 dark:bg-gray-900 flex justify-between items-center">
                <span class="text-lg font-semibold">AI Assistant</span>
                <button @click="getHint" class="bg-green-500 text-white px-4 py-2 rounded-lg">
                    Get Hint
                </button>
            </div>
            <div class="flex-1 p-4 bg-gray-100 dark:bg-gray-800 overflow-y-auto">
                <h2 class="text-md font-semibold mb-3">Hint</h2>
                <div class="markdown-content h-full">
                    <div v-html="compiledHint"></div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import { EditorView } from '@codemirror/view';
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';

export default {
    data() {
        return {
            questionMarkdown: '# Loading...',
            code: ``,
            output: "Click 'Run Code' to see output",
            aiHint: "Click 'Get Hint' for AI assistance...",
            editorView: null
        };
    },
    computed: {
        compiledMarkdown() {
            const md = new MarkdownIt({
                html: true,
                linkify: true,
                typographer: true,
                breaks: true
            });

            let rawHtml = md.render(this.questionMarkdown);
            rawHtml = rawHtml.replace(/<code>(.*?)<\/code>/g, '<code class="bg-gray-200 dark:bg-gray-700 text-sm px-1 py-0.5 rounded-md">$1</code>');
            return DOMPurify.sanitize(rawHtml);
        },
        compiledHint() {
            const md = new MarkdownIt({
                html: true,
                linkify: true,
                typographer: true,
                breaks: true
            });

            let rawHtml = md.render(this.aiHint);
            rawHtml = rawHtml.replace(/<code>(.*?)<\/code>/g, '<code class="bg-gray-200 dark:bg-gray-700 text-sm px-1 py-0.5 rounded-md">$1</code>');
            return DOMPurify.sanitize(rawHtml);
        }
    },
    mounted() {
        this.fetchQuestionMarkdown();
        this.fetchQuestionBoilerplate().then(() => {
            this.initCodeMirror();
        });
    },
    beforeUnmount() {
        if (this.editorView) {
            this.editorView.destroy();
        }
    },
    methods: {
        initCodeMirror() {
            if (this.editorView) return;

            const updateListener = EditorView.updateListener.of((update) => {
                if (update.docChanged) {
                    this.code = update.state.doc.toString();
                }
            });

            this.editorView = new EditorView({
                state: EditorState.create({
                    doc: this.code || '',  // Use existing code or empty string
                    extensions: [
                        basicSetup,
                        python(),
                        oneDark,
                        updateListener,
                        EditorView.theme({
                            "&": {
                                height: "100%",
                                minHeight: "100px"
                            },
                            ".cm-scroller": {
                                lineHeight: "1.6"
                            },
                            ".cm-content": {
                                padding: "10px 0"
                            }
                        })
                    ]
                }),
                parent: this.$refs.editorContainer
            });
        },

        updateEditorContent(newContent) {
            if (this.editorView) {
                const transaction = this.editorView.state.update({
                    changes: {
                        from: 0,
                        to: this.editorView.state.doc.length,
                        insert: newContent
                    }
                });
                this.editorView.dispatch(transaction);
            }
        },

        async fetchQuestionMarkdown() {
            const problemId = this.$route.params.id;
            const apiUrl = "http://localhost:8000";

            try {
                const response = await fetch(`${apiUrl}/problems/${problemId}/get_question_description/`, {
                    method: 'GET',
                    headers: { Accept: 'application/json' }
                });

                if (!response.ok) throw new Error(`Error: ${response.status}`);

                const data = await response.json();
                this.questionMarkdown = data.description || '# Error loading question.';
            } catch (error) {
                console.error('Failed to fetch question:', error);
                this.questionMarkdown = '# Unable to load question.';
            }
        },

        async fetchQuestionBoilerplate() {
            const problemId = this.$route.params.id;
            const apiUrl = "http://localhost:8000";

            try {
                const response = await fetch(`${apiUrl}/problems/${problemId}/get_question_boilerplate/`, {
                    method: 'GET',
                    headers: { Accept: 'application/json' }
                });

                if (!response.ok) throw new Error(`Error: ${response.status}`);

                const data = await response.json();
                this.code = data.boilerplate || '# Error code.';
                if (this.editorView) {
                    this.updateEditorContent(this.code);
                }
            } catch (error) {
                console.error('Failed to fetch code:', error);
                this.code = '# Unable to load code.';
                if (this.editorView) {
                    this.updateEditorContent(this.code);
                }
            }
        },

        async runCode() {
            const apiUrl = "http://localhost:8000/code_execution";

            this.output = "Running...";  // Show a loading message

            try {
                const response = await fetch(`${apiUrl}/execute/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ code: this.code })
                });

                if (!response.ok) throw new Error(`Execution error: ${response.status}`);

                const data = await response.json();
                this.output = data.output || "No output.";
            } catch (error) {
                console.error("Failed to execute code:", error);
                this.output = "Execution failed.";
            }
        },

        async getHint() {
            const apiUrl = "http://localhost:8000/ai_chat";

            this.aiHint = "Generating hint...";  // Show loading state

            try {
                const response = await fetch(`${apiUrl}/chat/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        question: this.questionMarkdown,
                        code: this.code,
                        output: this.output  // Now sending terminal output
                    })
                });

                if (!response.ok) throw new Error(`AI Hint error: ${response.status}`);

                const data = await response.json();
                console.log(data);
                this.aiHint = data.response || "No hint available.";
            } catch (error) {
                console.error("Failed to fetch AI hint:", error);
                this.aiHint = "Hint generation failed.";
            }
        }
    }
};
</script>

<style>
.markdown-content {
    @apply text-gray-800 dark:text-gray-200;
}

.markdown-content h1 {
    @apply text-4xl font-bold mb-6 mt-2;
}

.markdown-content h2 {
    @apply text-3xl font-bold mb-4 mt-6;
}

.markdown-content h3 {
    @apply text-2xl font-bold mb-3 mt-4;
}

.markdown-content p {
    @apply text-lg mb-4 leading-relaxed;
}

.markdown-content code {
    @apply bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono;
}

.markdown-content pre {
    @apply bg-gray-200 dark:bg-gray-700 p-4 rounded-lg my-4 overflow-x-auto;
}

.markdown-content pre code {
    @apply bg-transparent p-0;
}

.markdown-content ul {
    @apply list-disc list-inside mb-4 pl-4;
}

.markdown-content li {
    @apply mb-2;
}

.markdown-content hr {
    @apply my-6 border-t border-gray-300 dark:border-gray-600;
}

.cm-editor {
    height: 100% !important;
}

.cm-scroller {
    overflow: auto;
}
</style>
