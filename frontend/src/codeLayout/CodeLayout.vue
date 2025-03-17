<template>
    <div class="grid grid-cols-12 h-screen">
        <!-- Left Panel: Markdown Question -->
        <div class="col-span-3 bg-gray-100 dark:bg-gray-800 p-4 overflow-auto border-r">
            <h2 class="text-lg font-bold mb-2">Problem Statement</h2>
            <Markdown class="dark:bg-gray-800" :source="questionMarkdown" />
            <p>{{ questionMarkdown }}</p>
        </div>

        <!-- Middle Panel: Python Code Editor -->
        <div class="col-span-6 flex flex-col border rounded-lg overflow-hidden">
            <div class="p-2 bg-gray-200 dark:bg-gray-900 flex justify-between items-center">
                <span class="text-lg font-semibold">Python Code Editor</span>
                <button @click="runCode" class="bg-blue-500 text-white px-4 py-2 rounded-lg">
                    Run Code
                </button>
            </div>
            <div ref="editorContainer" class="h-[400px] border"></div>
            <div class="p-2 bg-gray-100 dark:bg-gray-800 h-40 overflow-auto">
                <h2 class="text-md font-semibold">Output</h2>
                <pre class="bg-gray-200 dark:bg-gray-900 p-2 rounded-md whitespace-pre-wrap">{{ output }}</pre>
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
            <div class="p-4 bg-gray-100 dark:bg-gray-800 h-[400px] overflow-auto">
                <h2 class="text-md font-semibold">Hint</h2>
                <pre class="bg-gray-200 dark:bg-gray-900 p-2 rounded-md whitespace-pre-wrap">{{ aiHint }}</pre>
            </div>
        </div>
    </div>
</template>

<script>
import * as Markdown from 'vue3-markdown-it';
import { EditorView } from '@codemirror/view';
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';

export default {
    components: { Markdown },
    data() {
        return {
            questionMarkdown: '# Loading...',
            code: ``,
            output: "Click 'Run Code' to see output",
            aiHint: "Click 'Get Hint' for AI assistance...",
            editorView: null
        };
    },
    mounted() {
        this.fetchQuestionMarkdown();
        this.fetchQuestionBoilerplate();
        this.initCodeMirror();
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
                    doc: this.code,
                    extensions: [basicSetup, python(), oneDark, updateListener]
                }),
                parent: this.$refs.editorContainer
            });
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
                console.log(data);
                this.code = data.boilerplate || '# Error code.';
            } catch (error) {
                console.error('Failed to fetch code:', error);
                this.questionMarkdown = '# Unable to load code.';
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
