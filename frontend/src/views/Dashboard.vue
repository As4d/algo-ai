<script setup>
import NotificationsWidget from '@/components/dashboard/NotificationsWidget.vue';
import StatsWidget from '@/components/dashboard/StatsWidget.vue';
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <StatsWidget />

        <div class="col-span-12 xl:col-span-12">
            <LeaderboardWidget />
        </div>
    </div>
</template>
