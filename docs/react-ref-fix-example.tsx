// 예시: alert-dialog.tsx의 올바른 ref 처리
import React from "react";

// Before (문제가 있는 코드)
function AlertDialogHeader({ className, ...props }: React.ComponentProps<"div">) {
  return <div {...props} />;
}

// After (올바른 해결책)
const AlertDialogHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  return (
    <div
      ref={ref}
      data-slot="alert-dialog-header"
      className={cn("flex flex-col gap-2 text-center sm:text-left", className)}
      {...props}
    />
  );
});
AlertDialogHeader.displayName = "AlertDialogHeader";
