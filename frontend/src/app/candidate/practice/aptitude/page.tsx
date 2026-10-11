import AptitudeInstructions from "./AptitudeInstructions";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function AptitudeInstructionsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const value = (input: string | string[] | undefined) => (Array.isArray(input) ? input[0] : input);

  return (
    <AptitudeInstructions
      companyType={value(params.companyType) || ""}
      experienceLevel={value(params.experienceLevel) === "Experienced" ? "Experienced" : "Fresher"}
      targetRole={value(params.targetRole) || "Software Engineer"}
    />
  );
}
