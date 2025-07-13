export default function MainScreen() {
	return (
		<div className="flex flex-col flex-1 min-h-0 bg-[var(--color-chat-background)]">
			<div className="flex justify-center items-center h-full">
				<div className="bg-[#2E2E38] text-white rounded-2xl p-6 text-center shadow-lg max-w-md">
					<p className="text-lg font-semibold">
						Open the sidebar to select an existing chat or create a new one.
					</p>
				 </div>
			</div>
		</div>
	);
}
