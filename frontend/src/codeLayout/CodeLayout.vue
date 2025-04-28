<template>
    <div class="grid grid-cols-12 h-screen">
        <!-- Left Panel: Markdown Question -->
        <div class="col-span-3 bg-gray-100 dark:bg-gray-800 p-6 overflow-auto">
            <div class="markdown-content">
                <div v-html="compiledMarkdown"></div>
            </div>
        </div>

        <!-- Middle Panel: Python Code Editor -->
        <div class="col-span-6 flex flex-col overflow-hidden h-full">
            <div class="p-2 bg-gray-200 dark:bg-gray-900 flex justify-between items-center">
                <span class="text-lg font-semibold">Python Code Editor</span>
                <div class="flex gap-2">
                    <button @click="runCode(false)" class="bg-blue-500 text-white px-4 py-2 rounded-lg">Run Code</button>
                    <button @click="runCode(true)" class="bg-green-500 text-white px-4 py-2 rounded-lg">Run Tests</button>
                </div>
            </div>
            <div ref="editorContainer" class="flex-1 min-h-0 overflow-hidden"></div>
            <div class="bg-gray-100 dark:bg-gray-800">
                <div class="p-2">
                    <!-- Output Section - Only show when not displaying test results -->
                    <div v-if="testResults.length === 0">
                        <h2 class="text-md font-semibold mb-2">Output</h2>
                        <pre class="bg-gray-200 dark:bg-gray-900 p-3 rounded-md whitespace-pre-wrap h-32 overflow-y-auto font-mono text-sm">{{ output }}</pre>
                    </div>

                    <!-- Test Results Section -->
                    <div v-if="testResults.length > 0">
                        <h2 class="text-md font-semibold mb-2">Test Results</h2>
                        <div class="max-h-[300px] overflow-y-auto">
                            <div v-for="(result, index) in testResults" :key="index" class="mb-2 p-2 rounded-md" :class="result.passed ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'">
                                <div class="flex justify-between items-center">
                                    <span class="font-medium">Test {{ index + 1 }}: {{ result.test_name }}</span>
                                    <span :class="result.passed ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                                        {{ result.passed ? 'Passed' : 'Failed' }}
                                    </span>
                                </div>
                                <div v-if="!result.passed" class="mt-2 text-sm">
                                    <div v-if="result.error" class="text-red-600 dark:text-red-400 whitespace-pre-wrap font-mono">{{ result.error }}</div>
                                    <div v-else>
                                        <div class="mb-1">
                                            <span class="font-medium">Expected:</span>
                                            <pre class="bg-gray-200 dark:bg-gray-700 p-1 mt-1 rounded">{{ result.expected_output }}</pre>
                                        </div>
                                        <div>
                                            <span class="font-medium">Got:</span>
                                            <pre class="bg-gray-200 dark:bg-gray-700 p-1 mt-1 rounded">{{ result.actual_output }}</pre>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Panel: AI Assistant -->
        <div class="col-span-3 flex flex-col overflow-hidden">
            <div class="p-2 bg-gray-200 dark:bg-gray-900 flex justify-between items-center">
                <span class="text-lg font-semibold">AI Assistant</span>
                <button @click="getHint" class="bg-green-500 text-white px-4 py-2 rounded-lg">Get Hint</button>
            </div>
            <div class="flex-1 p-4 bg-gray-100 dark:bg-gray-800 overflow-y-auto">
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
            editorView: null,
            testResults: [],
            startTime: null,
            timeSpent: 0
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
            this.startTime = Date.now();  // Start timing when problem loads
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
                    doc: this.code || '',
                    extensions: [
                        basicSetup,
                        python(),
                        oneDark,
                        updateListener,
                        EditorView.theme({
                            '&': {
                                height: '100%',
                                minHeight: '100px'
                            },
                            '.cm-scroller': {
                                lineHeight: '1.6'
                            },
                            '.cm-content': {
                                padding: '10px 0'
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
            const apiUrl = 'http://localhost:8000';

            try {
                const response = await fetch(`${apiUrl}/problems/${problemId}/description/`, {
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
            const apiUrl = 'http://localhost:8000';

            try {
                const response = await fetch(`${apiUrl}/problems/${problemId}/boilerplate/`, {
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

        async runCode(runTests = false) {
            const apiUrl = 'http://localhost:8000/code_execution';
            const problemId = this.$route.params.id;

            this.output = runTests ? '' : 'Running...';
            this.testResults = [];

            // Calculate time spent if running tests
            const timeSpent = runTests ? Math.floor((Date.now() - this.startTime) / 1000) : 0;

            try {
                const response = await fetch(`${apiUrl}/execute/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Accept: 'application/json'
                    },
                    credentials: 'include',  // Important for sending cookies
                    body: JSON.stringify({
                        code: this.code,
                        problem_id: problemId,
                        run_tests: runTests,
                        time_spent: timeSpent
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `Execution error: ${response.status}`);
                }

                if (data.test_results) {
                    this.testResults = data.test_results;
                    
                    // If all tests passed, reset the timer
                    if (data.all_tests_passed) {
                        this.startTime = Date.now();
                    }

                    // If it's not a test run but we got an error, show it in the output
                    if (!runTests && data.test_results[0]?.error) {
                        this.output = data.test_results[0].error;
                    }
                } else if (data.error) {
                    this.output = data.error;
                } else {
                    this.output = data.output || 'No output.';
                }
            } catch (error) {
                console.error('Failed to execute code:', error);
                this.output = error.message || 'An unknown error occurred';
                if (runTests) {
                    this.testResults = [{
                        test_name: "Code Execution",
                        passed: false,
                        error: error.message
                    }];
                }
            }
        },

        async getHint() {
            const apiUrl = 'http://localhost:8000/ai_chat';

            this.aiHint = 'Generating hint...'; // Show loading state

            try {
                const response = await fetch(`${apiUrl}/chat/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Accept: 'application/json'
                    },
                    credentials: 'include',  // Add this line to send cookies
                    body: JSON.stringify({
                        question: this.questionMarkdown,
                        code: this.code,
                        terminal: this.output
                    })
                });

                if (!response.ok) throw new Error(`AI Hint error: ${response.status}`);

                const data = await response.json();
                this.aiHint = data.response || 'No hint available.';
            } catch (error) {
                console.error('Failed to fetch AI hint:', error);
                this.aiHint = 'Hint generation failed.';
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
