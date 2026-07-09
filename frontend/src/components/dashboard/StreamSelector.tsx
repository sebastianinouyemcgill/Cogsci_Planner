import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { STREAM_ORDER } from "@/lib/dashboard-utils";

type StreamSelectorProps = {
  declaredStream: string | null;
  activeStream: string | null;
  isProvisional: boolean;
  provisionalStream: string | null;
  onDeclaredStreamChange: (stream: string | null) => void;
  onAcceptProvisional: () => void;
};

export function StreamSelector({
  declaredStream,
  activeStream,
  isProvisional,
  provisionalStream,
  onDeclaredStreamChange,
  onAcceptProvisional,
}: StreamSelectorProps) {
  return (
    <Card size="sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Stream</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <p className="text-lg font-semibold">{activeStream ?? "Not declared"}</p>
          {activeStream ? (
            <Badge variant={declaredStream ? "default" : "secondary"}>
              {declaredStream ? "Declared" : "Auto-selected"}
            </Badge>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Select
            value={declaredStream ?? "__none__"}
            onValueChange={(value) =>
              onDeclaredStreamChange(value === "__none__" ? null : value)
            }
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Change stream" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">Not declared</SelectItem>
              {STREAM_ORDER.map((streamName) => (
                <SelectItem key={streamName} value={streamName}>
                  {streamName}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {isProvisional && provisionalStream ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onAcceptProvisional}
            >
              Lock {provisionalStream}
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
