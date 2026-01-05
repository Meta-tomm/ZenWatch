'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCreateKeyword, useUpdateKeyword } from '@/hooks/use-keywords';
import type { Keyword } from '@/types';

const keywordSchema = z.object({
  keyword: z.string().min(2, 'Minimum 2 characters').max(50),
  category: z.string().min(1, 'Category required'),
  weight: z.number().min(1).max(5),
});

type KeywordFormData = z.infer<typeof keywordSchema>;

interface KeywordFormProps {
  keyword?: Keyword;
  onSuccess: () => void;
}

const CATEGORIES = [
  'healthtech',
  'blockchain',
  'dev',
  'ai',
  'cloud',
  'security',
];

export const KeywordForm = ({ keyword, onSuccess }: KeywordFormProps) => {
  const createMutation = useCreateKeyword();
  const updateMutation = useUpdateKeyword();

  const form = useForm<KeywordFormData>({
    resolver: zodResolver(keywordSchema),
    defaultValues: {
      keyword: keyword?.keyword ?? '',
      category: keyword?.category ?? 'dev',
      weight: keyword?.weight ?? 3,
    },
  });

  const onSubmit = async (data: KeywordFormData) => {
    try {
      if (keyword) {
        await updateMutation.mutateAsync({ id: keyword.id, data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onSuccess();
    } catch (error) {
      console.error('Error saving keyword:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="keyword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Keyword</FormLabel>
              <FormControl>
                <Input placeholder="e.g. FHIR, blockchain..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="category"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Category</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="weight"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Weight: {field.value}/5</FormLabel>
              <FormControl>
                <Slider
                  min={1}
                  max={5}
                  step={1}
                  value={[field.value]}
                  onValueChange={([value]) => field.onChange(value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-2">
          <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
            {keyword ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </Form>
  );
};
