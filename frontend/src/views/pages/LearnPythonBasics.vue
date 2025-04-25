<script setup>
import ProblemList from '@/components/ProblemList.vue';
</script>

<template>
    <ProblemList
        title="Learn Python Basics"
        problemType="python_basics"
        itemLabel="Topic"
        :sortByOrder="true"
    />
</template>